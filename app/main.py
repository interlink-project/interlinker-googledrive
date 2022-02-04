import json
import os
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

import app.crud as crud
from app.config import settings
from app.database import (
    AsyncIOMotorCollection,
    close_mongo_connection,
    connect_to_mongo,
    get_collection,
)
from app.google import delete_file, get_files
from app.googleservice import close_google_connection, connect_to_google, get_service
from app.model import (
    AssetBasicDataSchema,
    AssetCreateSchema,
    mime_type_options,
    mime_types,
)

domainfo = {
    "PROTOCOL": settings.PROTOCOL,
    "SERVER_NAME": settings.SERVER_NAME,
    "BASE_PATH": settings.BASE_PATH,
    "COMPLETE_SERVER_NAME": settings.COMPLETE_SERVER_NAME
}
app = FastAPI(
    title="Googledrive interlinker API", openapi_url=f"/openapi.json", docs_url="/docs", root_path=settings.BASE_PATH
)
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
app.add_event_handler("startup", connect_to_google)
app.add_event_handler("shutdown", close_google_connection)


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

mainrouter = APIRouter()


@mainrouter.get("/")
def main():
    return RedirectResponse(url=f"{settings.BASE_PATH}/docs")


@mainrouter.get("/healthcheck")
def healthcheck():
    return True


integrablerouter = APIRouter()


@integrablerouter.post("/assets", response_description="Add new asset", status_code=201)
async def create_asset(file: Optional[UploadFile] = File(...), collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    file_name = os.getcwd()+"/tmp/"+file.filename.replace(" ", "-")
    with open(file_name, 'wb+') as f:
        f.write(file.file.read())
        f.close()
    print(f"File saved in {file_name}")
    # optional because needs confirmation
    return await crud.create(collection, service, file_name)


@integrablerouter.get(
    "/assets/instantiate", response_description="GUI for asset creation"
)
async def instantiate_asset(request: Request):
    return templates.TemplateResponse("instantiator.html", {"request": request, "BASE_PATH": settings.BASE_PATH, "DOMAIN_INFO": json.dumps(domainfo)})


@integrablerouter.get(
    "/assets/{id}", response_description="Asset JSON", response_model=AssetBasicDataSchema
)
async def asset_data(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    if (asset := await crud.get(collection, service, id)) is not None:
        return asset
    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.delete("/assets/{id}", response_description="No content")
async def delete_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    if crud.get(collection, service, id) is not None:
        delete_result = await crud.delete(collection, service, id)
        if delete_result.deleted_count == 1:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.get(
    "/assets/{id}/view", response_description="GUI for interaction with asset"
)
async def asset_viewer(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    asset = await crud.get(collection, service, id)
    if asset is not None:
        return RedirectResponse(url=asset["webViewLink"])

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.post(
    "/assets/{id}/clone", response_description="Asset JSON", status_code=201
)
async def clone_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    if crud.get(collection, service, id) is not None:
        return await crud.clone(collection, service, id)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


# Custom endpoints (have a /api/v1 prefix)
customrouter = APIRouter()


@customrouter.post("/assets/empty", response_description="Asset JSON", status_code=201)
async def create_empty_asset(asset_in: AssetCreateSchema, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    mime_type = asset_in.mime_type
    name = asset_in.name
    if mime_type in mime_type_options:
        mime = mime_types[mime_type]
        return await crud.create_empty(collection, service, mime, name)
    raise HTTPException(
        status_code=400, detail=f"Mime type {mime_type} not in {mime_type_options}")


@customrouter.get(
    "/assets", response_description="List all assets"
)
async def list_assets(collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    return await crud.get_all(collection, service)


@customrouter.get(
    "/assets/{id}", response_description="Asset JSON"
)
async def show_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    asset = await crud.get(collection, service, id)
    if asset is not None:
        return asset

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@customrouter.post(
    "/assets/{id}/persist", response_description="Persist a temporal asset"
)
async def persist_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    if (asset := await crud.get(collection, service, id)):
        if asset["temporal"]:
            return await crud.update(collection, service, id, {"temporal": False})
        return asset
    raise HTTPException(status_code=404, detail=f"Asset {id} not found")

# TODO: Task to remove unused files


@customrouter.get("/clean")
async def clean_files(collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    assets = await crud.get_all(collection, service)
    for asset in assets:
        delete_file(service, asset["_id"])
        await crud.delete(collection, service, asset["_id"])
    return JSONResponse(status_code=status.HTTP_200_OK)


@customrouter.get("/files/real")
async def get_real_assets(service=Depends(get_service)):
    return JSONResponse(status_code=status.HTTP_200_OK, content=get_files(service))


@customrouter.get("/files/delete")
async def delete_unused_files(collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service)):
    assets = await crud.get_all(collection, service)
    assets_ids = [asset["_id"] for asset in assets]
    files = get_files(service)
    files_ids = [file["id"] for file in files]
    matches = [el for el in files_ids if el not in assets_ids]
    for id in matches:
        delete_file(service, id)
    return JSONResponse(status_code=status.HTTP_200_OK)

app.include_router(mainrouter, tags=["main"])
app.include_router(integrablerouter, tags=["Integrable"])
app.include_router(customrouter, prefix=settings.API_V1_STR, tags=["Custom endpoints"])

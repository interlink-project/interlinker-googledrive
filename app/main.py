import json
import os
from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
    Body
)
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

import app.crud as crud
from app import deps
from app.config import settings
from app.database import (
    AsyncIOMotorCollection,
    close_mongo_connection,
    connect_to_mongo,
    get_collection,
)
from app.google import delete_file, get_files
from app.googleservice import close_google_connection, connect_to_google, get_service
from app.info import info_data
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


@mainrouter.get("/info")
def main():
    return info_data


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
async def asset_data(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), user_id=Depends(deps.get_current_user_id)):
    if (asset := await crud.get(collection, service, id)) is not None:
        return asset
    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.delete("/assets/{id}", response_description="No content")
async def delete_asset(id: str, request: Request, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), token=Depends(deps.get_token_in_header)):
    if token != settings.BACKEND_SECRET:
        raise HTTPException(status_code=403)

    if await crud.get(collection, service, id) is not None:
        delete_file(service=service, id=id)
        delete_result = await crud.delete(collection, service, id)
        if delete_result.deleted_count == 1:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.get(
    "/assets/{id}/download", response_description="Asset file"
)
async def download_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), user_id=Depends(deps.get_current_user_id)):
    if (asset := await crud.get(collection, service, id)) is not None:
        if "webContentLink" in asset:
            return RedirectResponse(url=asset["webContentLink"])
        return JSONResponse({"error": "Could not download this resource. Try again later."})
    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.get(
    "/assets/{id}/view", response_description="GUI for interaction with asset"
)
async def asset_viewer(id: str, request : Request, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), user_id=Depends(deps.get_current_user_id)):
    user = await crud.get_user(id=user_id)
    asset = await crud.get(collection, service, id)
    if asset is not None:
        return templates.TemplateResponse("redirector.html", {"request": request, "BASE_PATH": settings.BASE_PATH, "DOMAIN_INFO": json.dumps(domainfo), "DATA": json.dumps({
            "redirectUrl": asset["webViewLink"],
            "user": user,
            "config": user.get(crud.INTERLINKER_NAME)
        })})

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.post(
    "/assets/{id}/clone", response_description="Asset JSON", status_code=201, response_model=AssetBasicDataSchema
)
async def clone_asset(id: str, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), user_id=Depends(deps.get_current_user_id)):
    if await crud.get(collection, service, id) is not None:
        return await crud.clone(collection, service, id)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@integrablerouter.post(
    "/assets/{id}/sync_users", response_description="Asset JSON", status_code=200
)
async def sync_users(id: str, request: Request, collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), payload: list = Body(...)):
    print(request.client.host)
    return await crud.sync_users(collection=collection, service=service, file_id=id, users_info=payload)


# Custom endpoints (have a /api/v1 prefix)
customrouter = APIRouter()


@customrouter.post("/setAdditionalEmails", status_code=200)
async def add_additional_emails(collection: AsyncIOMotorCollection = Depends(get_collection), service=Depends(get_service), emails: list = Body(...), user_id = Depends(deps.get_current_user_id)):
    config = await crud.get_user_config(user_id)
    config["additionalEmails"] = emails
    print(await crud.update_user_config(user_id, config))

    # update the existing files
    files = await crud.get_files_for_user(collection, user_id)
    for file in files:
        print(file)
        await crud.update_file_permissions(service=service, file_id=file.get("_id"), acl=file.get("acl"))

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

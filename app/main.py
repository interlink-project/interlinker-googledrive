import os
from typing import List

from fastapi import APIRouter, Body, FastAPI, File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

import app.crud as crud
from app.config import settings
from app.google import copy_file, create_file, delete_file, get_files
from app.model import AssetSchema

BASE_PATH = os.getenv("BASE_PATH", "")

app = FastAPI(
    title="Google Drive API Wrapper", openapi_url=f"/openapi.json", docs_url="/docs", root_path=BASE_PATH
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

"""
from fastapi_utils.tasks import repeat_every
@apirouter.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def repetitive_task() -> None:
    pass
    # clean(db)
"""

mainrouter = APIRouter()

@mainrouter.get("/")
def main():
    return RedirectResponse(url=f"{BASE_PATH}/docs")

@mainrouter.get("/healthcheck/")
def healthcheck():
    return True

specificrouter = APIRouter()

@specificrouter.get("/clean", response_description="Clean assets")
async def clean_files():
    assets = await crud.get_all()
    for asset in assets:
        delete_file(asset["_id"])
        await crud.delete(asset["_id"])
    return JSONResponse(status_code=status.HTTP_200_OK)

@specificrouter.get("/files/real", response_description="Get real files")
async def get_real_assets():
    return JSONResponse(status_code=status.HTTP_200_OK, content=get_files())

@specificrouter.get("/files/delete", response_description="Delete unused files")
async def delete_unused_files():
    assets = await crud.get_all()
    assets_ids = [asset["_id"] for asset in assets]
    files = get_files()
    files_ids = [file["id"] for file in files]
    matches = [el for el in files_ids if el not in assets_ids]
    for id in matches:
        delete_file(id)
    return JSONResponse(status_code=status.HTTP_200_OK)

defaultrouter = APIRouter()

@defaultrouter.post("/assets/", response_description="Add new asset", response_model=AssetSchema, status_code=201)
async def create_asset(file: UploadFile = File(...)):
    file_name = os.getcwd()+"/tmp/"+file.filename.replace(" ", "-")
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
    
    googlefile = create_file(file_name, "Copy")
    return await crud.create(googlefile)


@defaultrouter.get(
    "/assets/", response_description="List all assets", response_model=List[AssetSchema]
)
async def list_assets():
    return await crud.get_all()


@defaultrouter.get(
    "/assets/{id}", response_description="Get a single asset", response_model=AssetSchema
)
async def show_asset(id: str):
    asset = await crud.get(id)
    if asset is not None:
        return asset

    raise HTTPException(status_code=404, detail="Asset {id} not found")

@defaultrouter.post(
    "/assets/{id}/clone", response_description="Clone specific asset", response_model=AssetSchema, status_code=201
)
async def clone_asset(id: str):
    if crud.get(id) is not None:
        googlefile = copy_file("newTitle", id)
        return await crud.create(googlefile)

    raise HTTPException(status_code=404, detail="Asset {id} not found")


@defaultrouter.delete("/assets/{id}", response_description="Delete an asset")
async def delete_asset(id: str):
    if crud.get(id) is not None:
        delete_result = await crud.delete(id)
        if delete_result.deleted_count == 1:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail="Asset {id} not found")

@defaultrouter.get(
    "/assets/{id}/gui", response_description="GUI for specific asset"
)
async def gui_asset(id: str):
    asset = await crud.get(id)
    if asset is not None:
        return RedirectResponse(url=asset["webViewLink"])

    raise HTTPException(status_code=404, detail="Asset {id} not found")

app.include_router(mainrouter, tags=["main"])
app.include_router(defaultrouter, prefix=settings.API_V1_STR, tags=["default"])
app.include_router(specificrouter, prefix=settings.API_V1_STR, tags=["specific"])

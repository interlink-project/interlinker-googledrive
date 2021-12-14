from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.clean import clean
from app.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.database import db
from fastapi.responses import RedirectResponse
import os
from fastapi import File, UploadFile
from app.google import create_file, copy_file, get_files

app = FastAPI(
    title="Google Drive API Wrapper", openapi_url=f"{settings.API_V1_STR}/openapi.json", docs_url="/googledrive/docs"
)

try:
    os.mkdir("tmp")
except Exception as e:
    pass

clean()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # localhost only
        allow_methods=["*"],
        allow_headers=["*"],
    )

from fastapi_utils.tasks import repeat_every
@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def repetitive_task() -> None:
    pass
    # clean(db)

@app.get("/googledrive")
def main():
    return RedirectResponse(url="/googledrive/docs")

@app.get("/googledrive/healthcheck")
def healthcheck():
    return True

@app.get("/googledrive/api/v1/assets/real", response_description="Get real files")
async def get_real_assets():
    return JSONResponse(status_code=status.HTTP_200_OK, content=get_files())


@app.post("/googledrive/api/v1/assets/", response_description="Add new asset")
async def create_asset(file: UploadFile = File(...)):
    file_name = os.getcwd()+"/tmp/"+file.filename.replace(" ", "-")
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
    
    file = create_file(file_name, "Copy")
    file["_id"] = file["id"]
    del file["id"]
    asset = jsonable_encoder(file)
    new_asset = await db["assets"].insert_one(asset)
    created_asset = await db["assets"].find_one({"_id": new_asset.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_asset)


@app.get(
    "/googledrive/api/v1/assets/", response_description="List all assets"
)
async def list_assets():
    assets = await db["assets"].find().to_list(1000)
    return JSONResponse(status_code=status.HTTP_200_OK, content=assets)


@app.get(
    "/googledrive/api/v1/assets/{id}", response_description="Get a single asset"
)
async def show_asset(id: str):
    if (asset := await db["assets"].find_one({"_id": id})) is not None:
            return JSONResponse(status_code=status.HTTP_200_OK, content=asset)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")

@app.post(
    "/googledrive/api/v1/assets/{id}/clone", response_description="Clone specific asset"
)
async def clone_asset(id: str):
    if (asset := await db["assets"].find_one({"_id": id})) is not None:
        file = copy_file("newTitle", id)
        file["_id"] = file["id"]
        del file["id"]
        asset = jsonable_encoder(file)
        new_asset = await db["assets"].insert_one(asset)
        created_asset = await db["assets"].find_one({"_id": new_asset.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_asset)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")


@app.delete("/googledrive/api/v1/assets/{id}", response_description="Delete a asset")
async def delete_asset(id: str):
    delete_result = await db["assets"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")

@app.get(
    "/googledrive/api/v1/assets/{id}/gui", response_description="Clone specific asset"
)
async def gui_asset(id: str):
    if (asset := await db["assets"].find_one({"_id": id})) is not None:
        
        return RedirectResponse(url=asset["webViewLink"])

    raise HTTPException(status_code=404, detail=f"Asset {id} not found")

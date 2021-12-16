from app.database import db
from app.model import AssetSchema
from fastapi.encoders import jsonable_encoder

async def get(id: str):
    return await db["assets"].find_one({"_id": id})

async def get_all():
    return await db["assets"].find().to_list(1000)

async def create(googlefile: dict):
    googlefile["_id"] = googlefile["id"]
    print(googlefile)
    asset = AssetSchema(**googlefile)
    print(asset.__dict__)
    asset = jsonable_encoder(asset)
    print(asset)
    db_asset = await db["assets"].insert_one(asset)
    return await get(db_asset.inserted_id)

async def delete(id: str):
    return await db["assets"].delete_one({"_id": id})
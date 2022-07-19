from fastapi.encoders import jsonable_encoder
from app.google import get_file_by_id, copy_file, create_empty_file, create_file

async def get(collection, service, id: str):
    data = get_file_by_id(service, id)
    db_data = await collection.find_one({"_id": id})
    if not data or not db_data:
        return None
    data["temporal"] = db_data["temporal"]
    return data

async def get_all(collection, service):
    return await collection.find().to_list(1000)

async def common_create(collection, service, googlefile: dict, temporal=False):
    data = {
        "_id": googlefile["id"],
        "temporal": temporal
    }
    print(data)
    asset = jsonable_encoder(data)
    db_asset = await collection.insert_one(asset)
    return await get(collection, service, db_asset.inserted_id)

async def create(collection, service, filepath: str):
    googlefile = create_file(service, filepath)
    return await common_create(collection, service, googlefile)

async def clone(collection, service, id: str):
    asset = await get(collection, service, id)
    googlefile = copy_file(service, "Copy of " + asset["name"], id)
    return await common_create(collection, service, googlefile)

async def create_empty(collection, service, mime: str, name: str):
    googlefile = create_empty_file(service, mime, name)
    return await common_create(collection, service, googlefile)

async def update(collection, service, id: str, data):
    await collection.update_one( { "_id": id }, { "$set": data })
    return await get(collection, service, id)

async def sync_users(service, file_id, users_info):
    print(file_id, users_info)
    return

async def delete(collection, service, id: str):
    return await collection.delete_one({"_id": id})
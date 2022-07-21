from fastapi.encoders import jsonable_encoder
from app.google import get_file_by_id, copy_file, create_empty_file, create_file, get_permissions , remove_permission, add_permission
from app.database import get_users_collection

INTERLINKER_NAME = "googledrive"

async def get_user(id: str):
    collection = await get_users_collection()
    return await collection.find_one({"_id": id})

async def get_user_config(id: str):
    user = await get_user(id)
    return user.get(INTERLINKER_NAME, {})

async def update_user_config(id: str, data):
    collection = await get_users_collection()
    await collection.update_one( { "_id": id }, { "$set": {INTERLINKER_NAME: jsonable_encoder(data)} })
    return await get_user(id)

async def get_only_db(collection, id: str):
    return await collection.find_one({"_id": id})

async def get(collection, service, id: str):
    data = get_file_by_id(service, id)
    db_data = await collection.find_one({"_id": id})
    if not data or not db_data:
        return None
    data["temporal"] = db_data["temporal"]
    data["acl"] = db_data.get("acl", [])
    return data

async def get_all(collection, service):
    return await collection.find().to_list(1000)

async def common_create(collection, service, googlefile: dict, temporal=False):
    data = {
        "_id": googlefile["id"],
        "acl": [],
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
    await collection.update_one( { "_id": id }, { "$set": jsonable_encoder(data) })
    return await get(collection, service, id)

async def sync_users(collection, service, file_id, users_info):
    print("Syncing document users with", users_info)
    new_acl = []

    for user_entry in users_info:
        new_acl.append({
            "id": user_entry.get("id"),
            "email": user_entry.get("email")
        })

    await update(collection, service, file_id, {
        "acl": new_acl
    })

    await update_file_permissions(service, file_id, new_acl)


async def get_files_for_user(collection, user_id):
    return await collection.find({
        "acl": {
            "$elemMatch": {"id": user_id}}
        }
    ).to_list(1000)

async def update_file_permissions(service, file_id, acl):
    print("Updating permissions of", file_id)
    # clear permissions
    permissions = get_permissions(service, file_id)
    for permission in permissions:
        if not permission.get("role", "owner") == "owner":
            remove_permission(service, file_id, permission.get("id"))

    # create permissions based on the acl         
    for acl_entry in acl:
        """
        [
            {
                "id": ...
                "email": ...
            }
            ...
        ]
        """
        user : dict = await get_user(id=acl_entry.get("id"))
        add_permission(service, emails=[user.get("email")] + user.get(INTERLINKER_NAME, {}).get("additionalEmails", []), role="writer", file_id=file_id)
    return

async def delete(collection, service, id: str):
    return await collection.delete_one({"_id": id})
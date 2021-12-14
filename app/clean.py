from app.google import get_files, delete_file
from app.model import DriveAsset

def clean(db):
    print("Syncing (cleaning)")
    # Delete all files in drive that are not attached to any DriveAsset obj
    for i in get_files():
        obj = db.query(DriveAsset).filter(DriveAsset.drive_id == i["id"]).first()
        if not obj:
            delete_file(i["id"])
    return get_files()
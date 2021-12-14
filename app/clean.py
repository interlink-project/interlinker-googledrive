from app.google import get_files, delete_file

def clean():
    print("Syncing (cleaning)")
    # Delete all files in drive that are not attached to any DriveAsset obj
    for i in get_files():
        delete_file(i["id"])
    return get_files()
from app.googleservice import create_service


def set_public(service, file_id):
    user_permission = {
        'type': 'anyone',
        'role': 'writer',
    }
    perm = service.permissions().create(
        fileId=file_id,
        body=user_permission,
        fields='id',
    ).execute()
    return perm


def get_files(service, pageSize=1000, pageToken=None):
    results = service.files().list(
        pageSize=pageSize, pageToken=pageToken, orderBy="createdTime asc", fields=f"nextPageToken, files(id, createdTime)").execute()

    return results.get('nextPageToken', None), results.get('files', [])


service = create_service()

nextPageToken, files = get_files(service, 1000)
for file in files:
    try:
        print("Setting", file.get("id"), "public")
        set_public(service, file.get("id"))
    except:
        pass

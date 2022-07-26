# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py
from fastapi.exceptions import HTTPException
from apiclient.http import MediaFileUpload
import magic
import os
from app.model import fields


def get_files(service, pageSize=None):
    # https://developers.google.com/drive/api/v3/reference/files
    if pageSize:
        results = service.files().list(
            pageSize=pageSize, fields=f"nextPageToken, files({fields})").execute()
    else:
        results = service.files().list(fields=f"files({fields})").execute()
    return results.get('files', [])


def get_file_by_id(service, id):
    return service.files().get(fileId=id, fields=fields).execute()


def create_empty_file(service, mime_type, name):
    # TODO: if name contains extension, remove
    file_metadata = {
        'mimeType': mime_type,
        'name': name,
    }

    file = service.files().create(body=file_metadata,
                                  fields=fields).execute()
    set_public(service, file["id"])
    return file


def create_file(service, path):
    mime = magic.Magic(mime=True)
    mime = mime.from_file(path)
    media = MediaFileUpload(path,
                            mimetype=mime,
                            resumable=True)
    head, tail = os.path.split(path)
    file_metadata = {'name': tail}

    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields=fields).execute()
    if os.path.isfile(path):
        os.remove(path)
    else:  # Show an error ##
        raise Exception("Error: %s file not found" % path)

    set_public(service, file["id"])
    return file


def copy_file(service, name, id):
    body = {}
    if name:
        body["name"] = name
    try:
        file = service.files().copy(
            fileId=id, body=body, fields=fields).execute()
        set_public(service, file["id"])
        return file
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


def delete_file(service, id):
    service.files().delete(fileId=id).execute()

def set_public(service, file_id):
    user_permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    perm = service.permissions().create(
        fileId=file_id,
        body=user_permission,
        fields='id',
    ).execute()
    return perm

def get_permissions(service, file_id):
    return service.permissions().list(fileId=file_id, fields="*").execute().get("permissions", [])

def remove_permission(service, file_id, permission_id):
    return service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()

def add_permission(service, email, role, file_id):
    user_permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
    service.permissions().create(
        fileId=file_id,
        sendNotificationEmail=False,
        body=user_permission,
        fields='id',
    ).execute()
    
def clean(service):
    print("Syncing (cleaning)")
    # Delete all files in drive that are not attached to any DriveAsset obj
    for i in get_files(service):
        delete_file(service, i["id"])
    return get_files(service)

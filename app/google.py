# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py
from fastapi.exceptions import HTTPException
from apiclient.http import MediaFileUpload
import magic
import os
from app.model import fields
from apiclient import errors



def get_files(service, pageSize=1000, pageToken=None):
    # https://developers.google.com/drive/api/v3/reference/files
    if pageSize:
        results = service.files().list(
            pageSize=pageSize, pageToken=pageToken, fields=f"nextPageToken, files({fields})").execute()
    else:
        results = service.files().list(fields=f"files({fields})").execute()
    return results.get('nextPageToken', None), results.get('files', [])


def get_file_by_id(service, id):
   #print('- - -Obtiene el archivo desde su id')
   #print('- - -El id es: ', id)
   #print('- - -los fields are: ', fields)
   #print('- - -the service is:',service)
   
    try:
        file = service.files().get(fileId=id, fields=fields).execute()
       #print('- - -FileComplete::',file)
       #print('- - -Name:',file['name'])
        
        
        if(file['webViewLink']):
           #print('- - -webViewLink:',file['webViewLink'])
           pass
        else:
           #print('- - -WebContentLInk:',file['webContentLink'])
           pass
    except errors.HttpError as  error:
        print ('An error occurred:',error)



    #return service.files().get(fileId=id, fields=fields).execute()
    return file

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

def clone_file_readonly(service, name, id):
    body = {}
    if name:
        body["name"] = name
    try:
        file = service.files().copy(
            fileId=id, body=body, fields=fields).execute()
        set_readonly(service, file["id"])
        return file
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


def delete_file(service, id):
    service.files().delete(fileId=id).execute()

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

#Give just read permissions to a file:
def set_readonly(service, file_id):
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
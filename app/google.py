# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.http import MediaFileUpload
import magic

scope = ['https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)

# https://developers.google.com/drive/api/v3/quickstart/python
service = build('drive', 'v3', credentials=credentials)

fields = "id, name, webContentLink, webViewLink, thumbnailLink, version, mimeType, size, iconLink, createdTime, modifiedTime"

def get_files(pageSize = None):
    # https://developers.google.com/drive/api/v3/reference/files
    if pageSize:
        results = service.files().list(
            pageSize=pageSize, fields=f"nextPageToken, files({fields})").execute()
    else:
        results = service.files().list(fields=f"files({fields})").execute()
    return results.get('files', [])


def get_file_by_id(id):
    return service.files().get( fileId=id, fields=fields).execute()

def create_file(path, name):
    mime = magic.Magic(mime=True)
    mime = mime.from_file(path)
    media = MediaFileUpload(path,
                            mimetype=mime,
                            resumable=True)
    file_metadata = {'name': name}

    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields=fields).execute()
    set_public(file["id"])
    return file

def copy_file(newTitle, id):
    file = service.files().copy(
        fileId=id, body={'title': newTitle}, fields=fields).execute()
    set_public(file["id"])
    return file

def delete_file(id):
    return service.files().delete(fileId=id).execute()

def set_public(file_id):
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

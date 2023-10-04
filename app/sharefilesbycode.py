from fastapi import FastAPI, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fastapi import APIRouter, Depends, File, Query
import io
from googleapiclient.http import MediaIoBaseDownload
import openpyxl
from io import BytesIO
from fastapi.responses import StreamingResponse
import logging
from oauth2client.service_account import ServiceAccountCredentials
from app.config import GOOGLE_CREDENTIALS


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Constants for Excel columns
COL_STUDENT_CODE = 0
COL_CHILD_NAME = 1
COL_PARENT_NAME = 2


MIME_TYPE_EXTENSION_MAP = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/pdf": ".pdf",
    # Add other mime types and their associated extensions as required
}

GOOGLE_DOC_MIME_TYPES = {
    "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Add other Google Doc types and their standard MIME types as required
}


def initialize_drive_service():
    try:
        # Load Credentials
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)

        # Create the service in Google Drive
        return build('drive', 'v3', credentials=credentials)

    except Exception as e:
        logger.error(f"Error initializing Google Drive service: {str(e)}")
        return None


drive_service = initialize_drive_service()

#Look for a File in a Specific Folder.
def find_file_in_folder(folder_name: str, file_name: str):
    """Find a file inside a Google Drive folder."""
    folder_results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
    print("folder_results")
    print(folder_results)
    
    folders = folder_results.get('files', [])
    
    if not folders:
        return None
    
    for folder in folders:
        folder_id = folder['id']
        file_results = drive_service.files().list(q=f"'{folder_id}' in parents and name='{file_name}'", fields="files(id, name, mimeType)").execute()
        files = file_results.get('files', [])
        if files:
            return files[0] # Return the first file that matches
    return None


#Download the file with his name of a specific folder
async def download_file_from_drive_by_name(folder_name: str, file_name: str):
    """Download a file from Google Drive based on folder and file name."""
    file = find_file_in_folder(folder_name, file_name)
    
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_name} not found in folder {folder_name}")
    
    # Fetch the file metadata to get its mime type
    file_metadata = drive_service.files().get(fileId=file['id'], fields="mimeType").execute()
    mime_type = file_metadata.get('mimeType')
    
    # Check if the file is a Google document and needs exporting
    if mime_type in GOOGLE_DOC_MIME_TYPES:
        export_mime_type = GOOGLE_DOC_MIME_TYPES[mime_type]
        request = drive_service.files().export_media(fileId=file['id'], mimeType=export_mime_type)
        mime_type = export_mime_type  # Update mime type to the new exported type
    else:
        request = drive_service.files().get_media(fileId=file['id'])
    
    downloaded_file = io.BytesIO()
    downloader = MediaIoBaseDownload(downloaded_file, request)
    
    done = False
    while not done:
        _, done = downloader.next_chunk()

    downloaded_file.seek(0)
    return {
        "status": "success",
        "data": downloaded_file.read(),
        "file_name": file_name,
        "mime_type": mime_type
    }




def find_student_data(downloaded_file_content, student_code):
    """Find student data in the given Excel content."""
    workbook = openpyxl.load_workbook(filename=BytesIO(downloaded_file_content))
    worksheet = workbook.active
    for row in worksheet.iter_rows():
        print('La fila es:')
        print(row)

        # Accessing cell value using the index
        cell_value = row[0].value  # Assuming student_code is in the first column
        print('El valor de A1:')
        print(cell_value)

        if cell_value == student_code:
            print('Yes it is the code:')
            print(student_code)
            workbook.close()
            return {
                "resource_google_id": row[COL_STUDENT_CODE].value,
                "parent_name": row[COL_PARENT_NAME].value,
                "child_name": row[COL_CHILD_NAME].value
            }
    workbook.close()
    return None


#Obtain the Student Data
async def get_student_data(folder_name: str, file_name: str, student_code: str):

    # Remove the file extension from the student code, if present
    student_code = student_code.split('.')[0]
    
    downloaded_file_content = await download_file_from_drive_by_name(folder_name, file_name)

    data = find_student_data(downloaded_file_content["data"], student_code)
    if not data:
        raise HTTPException(status_code=404, detail="Student code not found in the spreadsheet")
    return data




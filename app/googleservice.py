import logging
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)

# https://developers.google.com/drive/api/v3/quickstart/python

class GoogleService:
    client = None

service = GoogleService()

async def get_service():
    return service.client

async def connect_to_google():
    logging.info("Connecting to Google Drive...")
    service.client = build('drive', 'v3', credentials=credentials)
    logging.info("Connected to google drive！")


async def close_google_connection():
    logging.info("Closing Google Drive connection...")
    service.client.close()
    logging.info("Google Drive closed！")

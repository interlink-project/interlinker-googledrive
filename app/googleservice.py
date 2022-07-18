import logging

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from app.config import GOOGLE_CREDENTIALS

scope = ['https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            GOOGLE_CREDENTIALS, scope)

# https://developers.google.com/drive/api/v3/quickstart/python


class GoogleService:
    client = None


service = GoogleService()


def create_service():
    serv = build('drive', 'v3', credentials=credentials)
    service.client = serv
    return serv


async def get_service():
    try:
        return service.client
    except:
        return create_service()


async def connect_to_google():
    logging.info("Connecting to Google Drive...")
    create_service()
    logging.info("Connected to google drive！")


async def close_google_connection():
    logging.info("Closing Google Drive connection...")
    service.client.close()
    logging.info("Google Drive closed！")

import secrets
from typing import List

from pydantic import AnyHttpUrl, BaseSettings
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    PROTOCOL: str
    SERVER_NAME: str
    BASE_PATH: str
    COMPLETE_SERVER_NAME: AnyHttpUrl = os.getenv("PROTOCOL") + os.getenv("SERVER_NAME") + os.getenv("BASE_PATH")

    MONGODB_URL: str
    MONGODB_DATABASE: str
    COLLECTION_NAME: str
    
    GOOGLE_PROJECT_ID: str
    GOOGLE_PRIVATE_KEY_ID: str
    GOOGLE_PRIVATE_KEY: str
    GOOGLE_CLIENT_EMAIL: str
    GOOGLE_CLIENT_ID: str
    
    class Config:
        case_sensitive = True

settings = Settings()

GOOGLE_CREDENTIALS = {
        "type": "service_account",
        "project_id":  settings.GOOGLE_PROJECT_ID,
        "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
        "private_key":  settings.GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
        "client_email":  settings.GOOGLE_CLIENT_EMAIL,
        "client_id":  settings.GOOGLE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/interlinker%40interlink-deusto.iam.gserviceaccount.com"
    }

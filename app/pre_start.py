import logging
import json
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
# google
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://www.googleapis.com/auth/drive']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 10

client = AsyncIOMotorClient(settings.MONGODB_URL)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def waitForDatabase() -> None:
    try:
        collection = client[settings.MONGODB_DATABASE][settings.COLLECTION_NAME]
        collection.find_one({"_id": "TEST"})
    except Exception as e:
        logger.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def waitForDrive() -> None:
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope)
        service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    credentials = {
        "type": "service_account",
        "project_id":  settings.GOOGLE_PROJECT_ID,
        "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
        "private_key":  settings.GOOGLE_PRIVATE_KEY,
        "client_email":  settings.GOOGLE_CLIENT_EMAIL,
        "client_id":  settings.GOOGLE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/interlinker%40interlink-deusto.iam.gserviceaccount.com"
    }
    with open("credentials.json", "w") as json_file:
        json.dump(credentials, json_file, indent=4)

    waitForDatabase()
    logger.info("Services finished initializing")
    client.close()


if __name__ == "__main__":
    main()

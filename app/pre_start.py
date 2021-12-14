import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

# google
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://www.googleapis.com/auth/drive']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 10


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def waitForDatabase() -> None:
    try:
        pass
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
    waitForDatabase()
    # waitForDrive()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    main()

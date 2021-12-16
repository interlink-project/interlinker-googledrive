import logging
import os
from app.google import clean

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    pass


def main() -> None:
    try:
        os.mkdir("tmp")
    except Exception as e:
        pass
    
    clean()
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import logging

logger: logging.Logger = logging.getLogger("01")
root_logger: logging.Logger = logging.getLogger()


def _basic_config() -> None:
    logging.basicConfig(format="%(message)s")


def setup_logging() -> None:
    env = os.environ.get("LOG_LEVEL", "").upper()
    if env == "DEBUG":
        _basic_config()
        logger.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    elif env == "INFO":
        _basic_config()
        logger.setLevel(logging.INFO)

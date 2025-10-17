import sys
from datetime import datetime

from loguru import logger

from .vars import LOGS_FOLDER


def setup_logger(debug=False):
    logger.remove()

    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # {today}.log
    logger.add(
        LOGS_FOLDER / f"{today}.log",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )

    # latest.log
    logger.add(
        LOGS_FOLDER / "latest.log",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        mode="w"
    )

    # Console
    logger.add(
        sys.stdout,
        level="DEBUG" if debug else "INFO",
        colorize=True
    )

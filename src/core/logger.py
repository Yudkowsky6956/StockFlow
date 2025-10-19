import sys
from datetime import datetime
import logging

import i18n
from loguru import logger

from .vars import LOGS_FOLDER, LOCALES_FOLDER


def formatter(record):
    time = f"<green>{record['time']:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    level = f"<level>{record['level']: <8}</level>"

    if record["level"].name not in ("INFO", "SUCCESS"):
        loc = f"<cyan>{record['name']}</cyan>:<cyan>{record['function']}</cyan>:<cyan>{record['line']}</cyan> - "
    else:
        loc = ""

    message = f"<level>{record['message']}</level>"

    module_name = record["extra"].get("module_name", "")
    module_color = record["extra"].get("module_color", "#FFFFFF")
    name = record["extra"].get("name", "")
    name_color = record["extra"].get("name_color", "#FFFFFF")

    extras = []
    if module_name:
        extras.append(f"<bold><fg {module_color}>{module_name:<11}</fg {module_color}></bold>")
    if name:
        extras.append(f"<fg {name_color}>{name:<8}</fg {name_color}>")

    extras_str = " | ".join(extras)
    if extras_str:
        extras_str = f" | {extras_str}"

    return f"{time} | {level}{extras_str} | {loc}{message}\n"


def setup_logger(debug=False):
    logger.remove()
    logging.getLogger("prefect").setLevel(logging.WARNING)

    LOCALES_FOLDER.mkdir(parents=True, exist_ok=True)
    i18n.load_path.append(str(LOCALES_FOLDER))

    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # {today}.log
    logger.add(
        LOGS_FOLDER / f"{today}.log",
        format = formatter,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )

    # latest.log
    logger.add(
        LOGS_FOLDER / "latest.log",
        format=formatter,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        mode="w"
    )

    # Console
    logger.add(
        sys.stdout,
        format=formatter,
        level="DEBUG" if debug else "INFO",
        colorize=True
    )

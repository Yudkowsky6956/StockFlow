from datetime import datetime
from pyrogram import Client
import i18n
from tqdm import tqdm
import asyncio
import socket
from loguru import logger
from src.core.global_config import get_global_config
from src.utils.hash import get_color_hash
import src.core.global_config as config
from .vars import LOGS_FOLDER, LOCALES_FOLDER
from src.core.secrets import get_env
from src.core.pyrogram.vars import ENV_API_ID, ENV_API_HASH, BOT_TOKEN
from src.core.pyrogram.vars import SESSION_FOLDER


def telegram_sink(record):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    notify_account = get_global_config().get("notify_account")
    with Client("stockflow_bot", get_env(ENV_API_ID), get_env(ENV_API_HASH), bot_token=get_env(BOT_TOKEN), workdir=SESSION_FOLDER) as client:
        client.send_message(notify_account, f"{socket.gethostname()} | {record}")


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
    name_color = get_color_hash(name)
    # second_module_name = record["extra"].get("second_module_name", "")
    # second_module_color = record["extra"].get("second_module_color", "#FFFFFF")

    extras = []
    if module_name:
        extras.append(f"<bold><fg {module_color}>{module_name:<11}</fg {module_color}></bold>")
    # if second_module_name:
    #     extras.append(f"<bold><fg {second_module_color}>{second_module_name:<11}</fg {second_module_color}></bold>")
    if name:
        extras.append(f"<fg {name_color}>{name:<8}</fg {name_color}>")

    extras_str = " | ".join(extras)
    if extras_str:
        extras_str = f" | {extras_str}"

    return f"{time} | {level}{extras_str} | {loc}{message}\n"


def setup_logger():
    logger.remove()

    LOCALES_FOLDER.mkdir(parents=True, exist_ok=True)
    i18n.load_path.append(str(LOCALES_FOLDER))
    i18n.set("locale", config.LANG)

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

    # Консоль
    logger.add(
        sink=lambda msg: tqdm.write(msg, end=""),
        format=formatter,
        level="DEBUG" if config.DEBUG else "INFO",
        colorize=True,
        enqueue=True,
    )
    if get_global_config().get("notify_on_critical"):
        # Telegram для CRITICAL
        logger.add(
            sink=telegram_sink,
            level="CRITICAL",
            enqueue=True
        )
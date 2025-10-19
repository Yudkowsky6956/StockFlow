import modulefinder

from loguru import logger
from prefect import flow

import argparse
import asyncio
from pathlib import Path

from src.core.logger import setup_logger
from src.core.pyrogram import Session, WrongAPIException, WrongPhoneException
from src.core.syntx import SyntxBot
from src.modules.modules import Veo, Sora, Runway
from src.core.pyrogram import set_api_id, set_api_hash


async def process_photo(prompt, photo):
    name = photo.stem
    log = logger.bind(name=name)
    veo_video = await Veo.generate(prompt, photo, logger=log)
    runway_video = await Runway.generate(prompt, photo, logger=log)


@flow
async def main_async(debug=False):
    setup_logger(debug)
    try:
        async with Session("89954254960") as client:
            bot = SyntxBot(client)
            await process_photo("котик и бабушка", Path("Moench_2339.jpg"))
    except WrongAPIException:
        logger.info("api wrong")
    except WrongPhoneException:
        logger.info("phone wrong")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enables debug-mode"
    )
    args = parser.parse_args()

    asyncio.run(main_async(debug=args.debug))

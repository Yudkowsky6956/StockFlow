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
from src.utils.hash import color_hash
from src.core.pyrogram import set_api_id, set_api_hash


@flow
async def process_photo(prompt, photo=None):
    if photo:
        name = photo.stem
    else:
        name = prompt
    name_color = color_hash(name)
    log = logger.bind(name=name, name_color=name_color)
    tasks = [asyncio.create_task(module.run(name, prompt, photo, logger=log)) for module in (Veo,)]
    return await asyncio.gather(*tasks)


async def main_async(debug=False):
    setup_logger(debug)
    try:
        async with Session("89954254960") as client:
            bot = SyntxBot(client)
            prompts = ["бабушка на скале", "бабушка в подъезде", "бабушка-гангстер"]
            tasks = [asyncio.create_task(process_photo(prompt)) for prompt in prompts]
            results = await asyncio.gather(*tasks)
            print(results)
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

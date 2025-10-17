from loguru import logger

import argparse
import asyncio

from src.core.logger import setup_logger
from src.core.pyrogram import Session, WrongAPIException, WrongPhoneException
from src.core.syntx import SyntxBot
from src.modules.veo import Veo
from src.core.pyrogram import set_api_id, set_api_hash


async def main_async(debug=False):
    setup_logger(debug)
    try:
        async with Session("89954254960") as client:
            bot = SyntxBot(client)
            for x in ["котик", "бабушка в подъезде", "земля"]:
                await Veo.generate(x)
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

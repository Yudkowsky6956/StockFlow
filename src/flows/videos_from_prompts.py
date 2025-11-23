import asyncio

from tqdm.asyncio import tqdm_asyncio
from loguru import logger as default_logger
from i18n import t

from src.core.syntx import SyntxBot
from src.core.database import Database
from src.interface.file_dialog import select_video_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow


class GenerateVideosFromPrompts(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gen_amount", "video_modules"]

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        destination = select_video_folder()
        amount = config.get("gen_amount")

        modules_names = config.get("video_modules")
        modules_objects = get_modules_objects(modules_names)

        database_name = config.get("database")
        with Database(database_name) as db:
            rows = db.get(amount=amount, modules=modules_names)

            bot = SyntxBot()
            async with bot.client:
                for row in rows:
                    name = row.hash
                    paraphrased = row.alt_prompt
                    for module in modules_objects:
                        config = module.get_config()
                        logger = default_logger.bind(name=name, module_name=config["name"], module_color=config["color"])
                        tasks.append(
                            asyncio.create_task(
                                module.run(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    prompt=paraphrased,
                                    destination=destination
                                )
                            )
                        )
                results = await tqdm_asyncio.gather(*tasks, desc=t(f"config_flows.{cls.__name__}.progress_bar"), unit=t(f"config_flows.{cls.__name__}.progress_unit"))
                return results
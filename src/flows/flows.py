import asyncio

from loguru import logger as default_logger

from src.core.syntx import SyntxBot
from src.core.database import Database
from src.interface.select import select_photos, select_video_folder
from src.modules import get_modules_objects
from .core_flow import Flow
from .config import FlowConfig


class GenerateVideosFromPrompts(Flow):
    @classmethod
    async def _run(cls, results: list, tasks: list, config: dict, database: Database) -> list:
        amount = FlowConfig.get_generations_amount(config)
        modules = config.get("modules")
        modules_objects = get_modules_objects(modules)
        rows = database.get(amount=amount, modules=modules)
        destination = select_video_folder()

        bot = SyntxBot()
        async with bot.client:
            for row in rows:
                name = row.hash
                paraphrased = row.alt_prompt
                for module in modules_objects:
                    logger = default_logger.bind(name=name, module=module)
                    tasks.append(
                        asyncio.create_task(
                            module.run(
                                name=name,
                                logger=logger,
                                database=database,
                                prompt=paraphrased,
                                destination=destination
                            )
                        )
                    )
            results = await asyncio.gather(*tasks)
            return results


class GenerateVideosFromPhotos(Flow):
    @classmethod
    async def _run(cls, results: list, tasks: list, config: dict, database: Database) -> list:
        modules = get_modules_objects(config.get("modules"))
        photos = select_photos()
        prompt = config.get("prompt")
        destination = select_video_folder()

        bot = SyntxBot()
        async with bot.client:
            for photo in photos:
                name = photo.stem
                for module in modules:
                    logger = default_logger.bind(name=name, module=module)
                    tasks.append(
                        asyncio.create_task(
                            module.run(
                                name=name,
                                logger=logger,
                                database=database,
                                photo=photo,
                                prompt=prompt,
                                destination=destination
                            )
                        )
                    )
            results = await asyncio.gather(*tasks)
            return results




import asyncio

from loguru import logger as default_logger

from src.core.database import Database
from src.core.syntx import SyntxBot
from src.interface.file_dialog import select_photos, select_video_folder
from src.modules import get_modules_objects
from .core_flow import Flow


class GenerateVideosFromPhotos(Flow):
    CONFIG_PARAMETERS = ["database", "prompt", "video_modules"]

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        modules_names = config.get("video_modules")
        modules_objects = get_modules_objects(modules_names)

        database_name = config.get("database")
        with Database(database_name) as db:
            photos = select_photos()
            prompt = config.get("prompt")
            destination = select_video_folder()

            bot = SyntxBot()
            async with bot.client:
                for photo in photos:
                    name = photo.stem
                    for module in modules_objects:
                        logger = default_logger.bind(name=name, module_name=module.syntx_name, module_color=module.color)
                        tasks.append(
                            asyncio.create_task(
                                module.run(
                                    name=name,
                                    logger=logger,
                                    photo=photo,
                                    prompt=prompt,
                                    destination=destination,
                                    database=db
                                )
                            )
                        )
                results = await asyncio.gather(*tasks)
                return results

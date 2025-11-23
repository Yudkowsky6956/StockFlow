import asyncio

from tqdm.asyncio import tqdm_asyncio
from loguru import logger as default_logger
from i18n import t

from src.core.syntx import SyntxBot
from src.core.database import Database
from src.interface.file_dialog import select_photo_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow


class GeneratePromptsPhotosVideos(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gen_amount", "upscale", "photo_modules", "video_modules"]

    @classmethod
    async def _task(cls, name, database, prompt, photo_module, video_modules, destination):
        results = []
        config = photo_module.get_config()
        logger = default_logger.bind(name=name, module_name=config["name"], module_color=config["color"])
        images = await photo_module.run(name=name, logger=logger, database=database, prompt=prompt, destination=destination)
        if images:
            for image in images:
                for video_module in video_modules:
                    config = video_module.get_config()
                    logger = default_logger.bind(name=name, module_name=config["name"], module_color=config["color"])
                    video = await video_module.run(name=name, prompt=prompt, photo=image, logger=logger, database=database, mark=False, destination=destination)
                    results.append(video)
        return results

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        destination = select_photo_folder()
        amount = config.get("gen_amount")
        photo_modules_names = config.get("photo_modules")
        photo_modules_objects = get_modules_objects(photo_modules_names)
        video_modules_names = config.get("video_modules")
        video_modules_objects = get_modules_objects(video_modules_names)

        database_name = config.get("database")
        with Database(database_name) as db:
            rows = db.get(amount=amount, modules=photo_modules_objects)

            bot = SyntxBot()
            async with bot.client:
                for row in rows:
                    name = row.hash
                    paraphrased = row.alt_prompt
                    for module in photo_modules_objects:
                        tasks.append(
                            asyncio.create_task(
                                cls._task(
                                    name=name,
                                    database=db,
                                    prompt=paraphrased,
                                    photo_module=module,
                                    video_modules=video_modules_objects,
                                    destination=destination
                                )
                            )
                        )
                results = await tqdm_asyncio.gather(*tasks, desc=t(f"config_flows.{cls.__name__}.progress_bar"), unit=t(f"config_flows.{cls.__name__}.progress_unit"))
                results = [x for row in results for x in row]
                return results
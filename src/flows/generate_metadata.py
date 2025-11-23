import asyncio

from tqdm.asyncio import tqdm_asyncio
from loguru import logger as default_logger
from i18n import t

from src.interface.file_dialog import select_photos
from src.interface.console_dialog import ask_double
from src.core.keywords import Keywords
from src.core.syntx import GenerationError, SyntxBot
from src.core.database import Database
from src.modules import get_modules_objects
from src.utils.sentances import wrap_by_words
from .core_flow import CoreFlow
from ..core.image_file import ImageFile


class GenerateMetadata(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gpt_template"]


    @classmethod
    async def _task(cls, name, image_file: ImageFile, logger, database, gpt_template, double):
        gpt = get_modules_objects("GPT")
        answer_dict = await gpt.run(
            name=name,
            logger=logger,
            database=database,
            prompt=gpt_template.format(keywords_amount=100 if double else 50),
            mark=False,
        )
        if answer_dict is None:
            return None
        if (not "description" in answer_dict) or (not "keywords" in answer_dict):
            raise GenerationError(t("error.gpt.no_parameter_in_result"))
        description = wrap_by_words(answer_dict.get("description"))
        keywords = Keywords(answer_dict.get("keywords")).run(double)
        image_file.title = description
        image_file.description = description
        image_file.keywords = keywords
        return image_file

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        photos = select_photos()
        gpt_template = config.get("gpt_template")

        double = ask_double()

        database_name = config.get("database")
        with Database(database_name) as db:
            gpt = get_modules_objects("GPT")
            photos = [ImageFile(photo) for photo in photos]

            bot = SyntxBot()
            async with bot.client:
                for photo in photos:
                    if not (photo.title or photo.description or photo.keywords):
                        name = photo.path.stem
                        config = gpt.get_config()
                        logger = default_logger.bind(name=name, module_name=config["name"], module_color=config["color"])
                        tasks.append(
                            asyncio.create_task(
                                cls._task(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    image_file=photo,
                                    gpt_template=gpt_template,
                                    double=double,
                                )
                            )
                        )
                results = await tqdm_asyncio.gather(*tasks, desc=t(f"config_flows.{cls.__name__}.progress_bar"), unit=t(f"config_flows.{cls.__name__}.progress_unit"))
                return results
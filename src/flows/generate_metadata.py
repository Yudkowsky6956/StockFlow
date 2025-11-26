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
    async def _task(cls, name, image_file: ImageFile, logger, database, gpt_template, double, gpt):
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
    async def _run(cls) -> list:
        default_logger.success(f"{t("info.flows.starting_flow")}: {t(f"config_flows.{cls.__name__}.choice")}")

        photos = select_photos()
        double = ask_double()

        flow_config = cls.get_config()
        gpt_template = flow_config.get("gpt_template")
        database_name = flow_config.get("database")
        unit = t(f"config_flows.{cls.__name__}.progress_unit")

        tasks = []
        gpt = get_modules_objects("GPT")
        module_name = gpt.get_name()
        module_color = gpt.get_color()
        photos = [ImageFile(photo) for photo in photos]

        with Database(database_name) as db:
            async with SyntxBot().client:
                for photo in photos:
                    if not (photo.title or photo.description or photo.keywords):
                        name = photo.path.stem
                        logger = default_logger.bind(name=name, module_name=module_name, module_color=module_color)

                        tasks.append(
                            asyncio.create_task(
                                cls._task(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    image_file=photo,
                                    gpt_template=gpt_template,
                                    double=double,
                                    gpt=gpt
                                )
                            )
                        )

                return await tqdm_asyncio.gather(
                    *tasks,
                    desc=f"{module_name:<11}",
                    unit=unit
                )
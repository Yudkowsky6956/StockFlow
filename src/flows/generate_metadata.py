import asyncio
import traceback
from dotenv import load_dotenv

from i18n import t
from loguru import logger as default_logger
from tqdm.asyncio import tqdm_asyncio

from src.core.database import Database
from src.core.global_config import get_global_config
from src.core.image_file import ImageFile
from src.core.keywords import Keywords
from src.core.logger import telegram_sink
from src.core.stop_event import StopEvent
from src.core.syntx import GenerationError, SyntxBot
from src.interface.async_console_dialog import ask_double
from src.interface.file_dialog import select_photos
from src.modules import get_modules_objects
from src.utils.sentances import wrap_by_words
from .core_flow import CoreFlow

import re

load_dotenv()

class GenerateMetadata(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gpt_template", "openai_gpt"]

    phrases = [
        "The image shows",
        "The image features",
        "The image showcases",
        "The image depicts",
        "The image presents",
        "The scene features",
        "The scene showcases",
        "The scene shows",
        "The scene displays",
        "The scene depicts",
        "The close-up image",
        "The image",
    ]

    @staticmethod
    def remove_phrases(text, phrases):
        pattern = r"\b(?:" + "|".join(re.escape(p) for p in phrases) + r")\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @classmethod
    async def _task(cls, name, image_file: ImageFile, logger, database, gpt_template, double, gpt):
        answer_dict = await gpt.run(
            name=name,
            photo=image_file.path,
            logger=logger,
            database=database,
            prompt=gpt_template.format(keywords_amount=100 if double else 50),
            mark=False,
        )
        if answer_dict is None:
            return None
        if (not "description" in answer_dict) or (not "keywords" in answer_dict):
            logger.error(t("error.gpt.no_parameter_in_result"))
            return
        description = cls.remove_phrases(wrap_by_words(answer_dict.get("description")), cls.phrases)
        keywords = Keywords(answer_dict.get("keywords")).run(double)
        image_file.title = description
        image_file.description = description
        image_file.keywords = keywords
        return image_file

    @classmethod
    async def _run(cls) -> list:
        default_logger.success(f"{t("info.flows.starting_flow")}: {t(f"config_flows.{cls.__name__}.choice")}")

        photos = select_photos()
        double = await ask_double()

        flow_config = cls.get_config()
        gpt_template = flow_config.get("gpt_template")
        database_name = flow_config.get("database")
        unit = t(f"config_flows.{cls.__name__}.progress_unit")
        use_openai_gpt = flow_config.get("openai_gpt")

        tasks = []
        gpt = get_modules_objects("OpenAIGPT" if use_openai_gpt else "GPT")
        module_name = gpt.get_name()
        module_color = gpt.get_color()
        photos = [ImageFile(photo) for photo in photos]
        await cls._reset_modules([gpt])

        try:
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

                    async def _watch_for_stop(tasks):
                        await StopEvent.event.wait()
                        for task in tasks:
                            task.cancel()
                    stop_watcher = asyncio.create_task(_watch_for_stop(tasks))

                    try:
                        result = await tqdm_asyncio.gather(
                            *tasks,
                            desc=f"{module_name:<11}",
                            unit=unit
                        )
                        if get_global_config().get("notify_on_end"):
                            telegram_sink(t("info.flows.flow_ended").format(name=t(f"config_flows.{cls.__name__}.choice")))
                        return result
                    except asyncio.CancelledError:
                        pass
                    finally:
                        stop_watcher.cancel()

        except Exception as e:
            default_logger.critical(str(e))
            traceback.print_exc()
            return []


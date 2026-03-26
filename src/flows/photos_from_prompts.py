import asyncio
import traceback

from i18n import t
from loguru import logger as default_logger
from tqdm.asyncio import tqdm_asyncio

from src.core.database import Database
from src.core.global_config import get_global_config
from src.core.logger import telegram_sink
from src.core.stop_event import StopEvent
from src.core.syntx import GenerationError, SyntxBot
from src.interface.file_dialog import select_photo_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow


class GeneratePhotosFromPrompts(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gen_amount", "upscale", "photo_modules"]


    @classmethod
    async def _run(cls) -> list:
        default_logger.success(f"{t("info.flows.starting_flow")}: {t(f"config_flows.{cls.__name__}.choice")}")

        destination = select_photo_folder()

        flow_config = cls.get_config()
        amount = flow_config.get("gen_amount")
        modules_names = flow_config.get("photo_modules")
        database_name = flow_config.get("database")

        unit = t(f"config_flows.{cls.__name__}.progress_unit")

        modules = get_modules_objects(modules_names)
        await cls._reset_modules(modules)
        tasks = []
        results = []

        try:
            with Database(database_name) as db:
                all_rows = db.get(amount=amount, modules=modules_names)

                async with SyntxBot().client:
                    for module in modules:
                        module_name = module.get_name()
                        module_color = module.get_color()
                        module_rows = all_rows[module_name]
                        module_tasks = []

                        for row in module_rows:
                            name = row.hash
                            paraphrased = row.alt_prompt
                            logger = default_logger.bind(name=name, module_name=module_name, module_color=module_color)

                            module_tasks.append(
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

                        tasks.append(
                            asyncio.create_task(
                                tqdm_asyncio.gather(
                                    *module_tasks,
                                    desc=f"{module_name:<11}",
                                    unit=unit
                                )
                            )
                        )

                    async def _watch_for_stop(tasks):
                        await StopEvent.event.wait()
                        for task in tasks:
                            task.cancel()
                    stop_watcher = asyncio.create_task(_watch_for_stop(tasks))

                    try:
                        nested_results = await asyncio.gather(*tasks)
                        for result in nested_results:
                            if not isinstance(result, list):
                                result = [result]
                            results.extend(result)
                        if get_global_config().get("notify_on_end"):
                            telegram_sink(t("info.flows.flow_ended").format(name=t(f"config_flows.{cls.__name__}.choice")))
                        return results
                    except asyncio.CancelledError:
                        pass
                    finally:
                        stop_watcher.cancel()

        except Exception as e:
            default_logger.critical(str(e))
            traceback.print_exc()
            return []

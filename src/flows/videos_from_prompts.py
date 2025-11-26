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
    async def _run(cls) -> list:
        default_logger.success(f"{t("info.flows.starting_flow")}: {t(f"config_flows.{cls.__name__}.choice")}")

        destination = select_video_folder()

        flow_config = cls.get_config()
        amount = flow_config.get("gen_amount")
        modules_names = flow_config.get("video_modules")
        database_name = flow_config.get("database")
        unit = t(f"config_flows.{cls.__name__}.progress_unit")

        modules = get_modules_objects(modules_names)
        tasks = []
        results = []

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

                nested_results = await asyncio.gather(*tasks)
                for result in nested_results:
                    results.extend(result)
                return results
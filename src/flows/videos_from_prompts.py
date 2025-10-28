import asyncio

from loguru import logger as default_logger

from src.core.syntx import SyntxBot
from src.core.database import Database
from src.interface.file_dialog import select_video_folder
from src.interface.console_dialog import ask_generation_amount
from src.modules import get_modules_objects
from .core_flow import Flow


class GenerateVideosFromPrompts(Flow):
    @classmethod
    async def _run(cls, tasks: list, config: dict, database: Database) -> list:
        amount = ask_generation_amount()
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
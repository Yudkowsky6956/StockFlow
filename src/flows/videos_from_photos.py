import asyncio

from loguru import logger as default_logger

from src.interface.console_dialog import ask_database, ask_amount
from src.core.syntx import SyntxBot
from src.core.database import Database
from src.interface.file_dialog import select_photos, select_video_folder
from src.modules import get_modules_objects
from .core_flow import Flow


class GenerateVideosFromPhotos(Flow):
    @classmethod
    def get_settings_choices(cls):
        return super().get_settings_choices() | {
            cls.get_config_parameter_locale("database", "name"):
                lambda: cls.set_property(
                    parameter="database",
                    long_instruction=cls.get_config_parameter_locale("database", "description"),
                    func=ask_database
                ),
            cls.get_config_parameter_locale("amount", "name"):
                lambda: cls.set_property(
                    parameter="amount",
                    long_instruction=cls.get_config_parameter_locale("amount", "description"),
                    func=ask_amount
                ),
            cls.get_config_parameter_locale("modules", "name"):
                lambda: cls.set_property(
                    parameter="modules",
                    long_instruction=cls.get_config_parameter_locale("amount", "description"),
                    func=ask_amount
                ),
        }

    @classmethod
    async def _run(cls, tasks: list, config: dict, database: Database) -> list:
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

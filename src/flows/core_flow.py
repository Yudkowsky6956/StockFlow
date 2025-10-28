import asyncio
from i18n import t

import yaml
from loguru import logger

from src.interface import Menu
from src.core.database import Database
from src.interface.console_dialog import ask_database
from .vars import FLOWS_YML


class Flow:
    NAME = "flow"

    @classmethod
    def run(cls) -> list:
        """
        Синхронная точка входа в сценарий.

        :return: Список результатов сценария.
        """
        tasks = []
        config = cls.get_config()
        db_name = ask_database()
        database = Database(db_name)

        return asyncio.run(cls._run(tasks, config, database))

    @classmethod
    async def _run(cls, tasks: list, config: dict, database: Database) -> list:
        """
        Backend-функция входа в сценарий, которую нужно перегружать в дочерних функциях.

        :param tasks: Список задач сценария.
        :param config: Конфигурация сценария.
        :param database: База данных сценария.
        :return: Список результатов сценария.
        """

    @classmethod
    def get_config(cls) -> dict:
        """
        Загружает конфиг для данного сценария.

        :return: Словарь конфига сценария.
        """
        return cls.get_global_config()[cls.__name__]

    @classmethod
    def get_global_config(cls) -> dict:
        return yaml.safe_load(FLOWS_YML.read_text(encoding="utf-8"))

    @classmethod
    def set_global_config(cls, config: dict):
        with FLOWS_YML.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    @classmethod
    def run_menu(cls):
        class ConfigMenu(Menu):
            name = cls.get_menu_settings_path()
            choices_map = cls.get_settings_choices()
        return ConfigMenu.run()

    @classmethod
    def set_database(cls, long_instruction=None):
        if long_instruction:
            long_instruction = t(long_instruction)
        config = cls.get_global_config()
        config[cls.__name__]["database"] = ask_database(default=config.get("database"), long_instruction=long_instruction, back=True)
        cls.set_global_config(config)

    @classmethod
    def set_property(cls, parameter, func, long_instruction=None):
        if long_instruction:
            long_instruction = t(long_instruction)
        config = cls.get_global_config()
        config[cls.__name__][parameter] = func(default=config.get(parameter), long_instruction=long_instruction, back=True)
        cls.set_global_config(config)


    @classmethod
    def get_settings_choices(cls):
        return {
            "menu.back": "back"
        }

    @classmethod
    def get_choices_with_data(cls):
        config = cls.get_config()
        return {config.get(choice, choice): value for choice, value in cls.get_settings_choices()}

    @classmethod
    def get_config_parameter_locale(cls, *args) -> str:
        default = f"config.default"
        attribute = f"config.{cls.__name__}"

        parameter = ".".join(args)

        attribute_parameter = f"{attribute}.{parameter}"
        default_parameter = f"{default}.{parameter}"

        if t(attribute_parameter) == attribute_parameter:
            return default_parameter
        else:
            return attribute_parameter

    @classmethod
    def get_name_locale(cls):
        return f"{cls.get_config_locale()}.name"

    @classmethod
    def get_choice_locale(cls):
        return f"{cls.get_config_locale()}.choice"

    @classmethod
    def get_config_locale(cls):
        return f"config.{cls.__name__}"

    @classmethod
    def get_menu_settings_path(cls):
        return f"{cls.get_name_locale()}"






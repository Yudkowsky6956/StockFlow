import asyncio
import inspect

import yaml
from i18n import t

from src.interface import Menu
from src.interface.console_dialog import ask_database, ask_generation_amount, ask_string, ask_video_modules
from .vars import FLOWS_YML
from src.modules import ALL_MODULES


class Flow:
    NAME = "flow"

    DEFAULT_CHOICE: dict = {"menu.back": "back"}
    CONFIG_PARAMETERS = []
    ASK_HANDLERS = {
        "database": ask_database,
        "gen_amount": ask_generation_amount,
        "video_modules": ask_video_modules,
        "prompt": ask_string,
        "pre_template": ask_string,
        "post_template": ask_string
    }

    @classmethod
    def run(cls) -> list:
        """
        Синхронная точка входа в сценарий.
        Возвращает список результатов сценария.
        """
        tasks = []
        config = cls.get_config()
        result = asyncio.run(cls._run(tasks, config))
        return result

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        """
        Backend-функция входа в сценарий, которую нужно перегружать в дочерних функциях.

        :param tasks: Список задач сценария.
        :param config: Конфигурация сценария.
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
    def get_settings_choices(cls):
        choices = cls.DEFAULT_CHOICE.copy()
        for parameter in cls.CONFIG_PARAMETERS:
            name = cls.get_config_parameter_locale(parameter, "name")
            description = cls.get_config_parameter_locale(parameter, "description")
            choices[name] = lambda p=parameter, d=description: cls.set_property(parameter=p, description=d)
        return choices

    @classmethod
    def set_property(cls, parameter: str, description: str = None):
        """
        Универсальный метод для установки свойства через соответствующий ask-интерфейс.
        """
        if description:
            description = t(description)

        config = cls.get_global_config()
        local_config = config.setdefault(cls.__name__, {})

        ask_fn = cls.ASK_HANDLERS.get(parameter)
        if not ask_fn:
            raise ValueError(f"Неизвестный параметр: {parameter}")

        # Определяем, поддерживает ли функция параметр 'back'
        sig = inspect.signature(ask_fn)
        kwargs = {
            "default": local_config.get(parameter),
            "long_instruction": description,
        }
        if "back" in sig.parameters:
            kwargs["back"] = True

        new_value = ask_fn(**kwargs)

        local_config[parameter] = new_value
        cls.set_global_config(config)

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






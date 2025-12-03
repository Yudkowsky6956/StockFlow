import inspect

import yaml
from i18n import t

from src.interface import Menu
from src.interface.console_dialog import ask_database, ask_generation_amount, ask_not_negative_float, \
    ask_not_negative_integers, ask_photo_modules, ask_string, ask_video_modules, ask_yes_no


class SettingsMixin:
    menu_config_name = "TEMP"
    CONFIG_PATH = None
    CONFIG_PARAMETERS = []
    ASK_HANDLERS = {
        "database": ask_database,
        "gen_amount": ask_generation_amount,
        "video_modules": ask_video_modules,
        "prompt": ask_string,
        "pre_template": ask_string,
        "post_template": ask_string,
        "photo_modules": ask_photo_modules,
        "upscale": ask_yes_no,
        "name": ask_string,
        "color": ask_string,
        "timeout": ask_not_negative_integers,
        "batch_size": ask_not_negative_integers,
        "flags": ask_string,
        "one_video_per_photo": ask_yes_no,
        "telegram_account": ask_string,
        "notify_account": ask_string,
        "notify_on_critical": ask_yes_no,
        "notify_on_end": ask_yes_no,
        "delay_normal": ask_not_negative_float,
        "delay_spread": ask_not_negative_float,
    }

    @classmethod
    def get_config(cls) -> dict:
        """
        Загружает конфиг для данного сценария.

        :return: Словарь конфига сценария.
        """
        return cls.get_global_config()[cls.__name__]

    @classmethod
    def get_global_config(cls) -> dict:
        return yaml.safe_load(cls.CONFIG_PATH.read_text(encoding="utf-8"))

    @classmethod
    def set_global_config(cls, config: dict):
        with cls.CONFIG_PATH.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    @classmethod
    def run_menu(cls):
        class ConfigMenu(Menu):
            name = cls.menu_config_name
            mixin = cls
            choices = cls.get_settings_choices()

            @classmethod
            def get_name(cls):
                return t(f"config_{cls.name}.{cls.mixin.__name__}.name")

            @classmethod
            def get_item_choice_locale(cls, item):
                return item

            @classmethod
            def get_item_name_locale(cls, item):
                return item
        return ConfigMenu.run_menu()

    @classmethod
    def get_settings_choices(cls):
        choices = {}
        for parameter in cls.CONFIG_PARAMETERS:
            name = cls.get_config_parameter_locale(parameter, "name")
            message = cls.get_config_parameter_locale(parameter, "message")
            description = cls.get_config_parameter_locale(parameter, "description")
            choices[name] = lambda p=parameter, m=message, d=description: cls.set_property(parameter=p, message=m, description=d)
        return choices

    @classmethod
    def set_property(cls, parameter: str, message: str = None, description: str = None):
        """
        Универсальный метод для установки свойства через соответствующий ask-интерфейс.
        """
        if message:
            message = t(message)
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
            "message": message,
            "long_instruction": description,
            "default": local_config.get(parameter)
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
    def get_config_locale(cls):
        return f"config_{cls.menu_config_name}"

    @classmethod
    def get_config_parameter_locale(cls, *args) -> str:
        default = f"{cls.get_config_locale()}.default"
        attribute = f"{cls.get_config_locale()}.{cls.__name__}"

        parameter = ".".join(args)

        attribute_parameter = f"{attribute}.{parameter}"
        default_parameter = f"{default}.{parameter}"

        if t(attribute_parameter) == attribute_parameter:
            return default_parameter
        else:
            return attribute_parameter
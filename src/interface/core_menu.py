import asyncio
import inspect
import sys

from InquirerPy import inquirer
from i18n import t

from src.utils.console import clear_last_lines


class Menu:
    current_path = []
    BACK = "menu.back"
    EXIT = "menu.exit"
    BACK_CHOICE = {BACK: "back"}
    EXIT_CHOICE = {EXIT: "exit"}
    SOURCE = False

    name = "NAME"
    choices = {}

    default_choice = None

    @classmethod
    def get_choices_list(cls):
        return list(cls.get_choices_map().keys())

    @classmethod
    def get_choices_map(cls):
        choices_map = {
            cls.get_item_choice_locale(choice): attr if attr else choice for choice, attr in cls.choices.items()
        }
        if not cls.SOURCE:
            choices_map = cls.BACK_CHOICE | choices_map
        else:
            choices_map = choices_map | cls.EXIT_CHOICE
        choices_map = {t(key): value for key, value in choices_map.items()}
        return choices_map

    @classmethod
    def get_message(cls):
        return f"{" ❯ ".join([t(element) for element in cls.current_path])}:"

    @classmethod
    def run_menu(cls):
        """Функция вызова меню."""
        cls.current_path.append(cls.get_name())
        message = cls.get_message()
        choices = cls.get_choices_list()

        while True:
            try:
                sys.stdout.flush()
                choice = inquirer.select(
                    message=message,
                    choices=choices,
                    default=cls.default_choice or choices[0],
                ).execute()
                clear_last_lines(amount=1)

                if choice == t(cls.BACK):
                    break
                elif choice == t(cls.EXIT):
                    return

                action = cls.get_choices_map().get(choice)
                if callable(action):
                    if inspect.iscoroutinefunction(action):
                        asyncio.run(action())
                    else:
                        action()

            except KeyboardInterrupt:
                pass
        cls.current_path.remove(cls.get_name())

    @classmethod
    def get_name(cls):
        return t(f"menu.{cls.name}.name")

    @classmethod
    def get_item_choice_locale(cls, item):
        return f"menu.{item.name}.choice"

    @classmethod
    def get_item_name_locale(cls, item):
        return f"menu.{item.name}.name"


class ConfigurableMenu(Menu):
    @classmethod
    def get_item_choice_locale(cls, item):
        return f"config_{cls.name}.{item.__name__}.choice"

    @classmethod
    def get_item_name_locale(cls, item):
        return f"config_{cls.name}.{item.__name__}.name"


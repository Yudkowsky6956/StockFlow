from i18n import t
from InquirerPy import inquirer

import inspect

from loguru import logger

from src.utils.console import clear_last_lines


class Menu:
    current_path = []
    BACK = "menu.back"
    DEFAULT_CHOICES = {BACK: "back"}

    name = "NAME"
    choices_map = {}
    default_choice = None

    @classmethod
    def get_choices(cls):
        return [t(choice) for choice in cls.choices_map.keys()]

    @classmethod
    def get_choices_map(cls):
        return {t(key): value for key, value in cls.choices_map.items()}

    @classmethod
    def get_message(cls):
        return f"{" ❯ ".join([t(element) for element in cls.current_path])}:"

    @classmethod
    def run(cls, backing=False):
        """Функция вызова меню."""
        if not backing:
            cls.current_path.append(cls.name)
        message = cls.get_message()
        choices = cls.get_choices()

        while True:
            try:
                choice = inquirer.select(
                    message=message,
                    choices=choices,
                    default=cls.default_choice or choices[0],
                ).execute()
                clear_last_lines(amount=1)

                action = cls.get_choices_map().get(choice)
                if callable(action):
                    action()
                elif action == "back":
                    break
            except KeyboardInterrupt:
                pass
        cls.current_path.remove(cls.name)
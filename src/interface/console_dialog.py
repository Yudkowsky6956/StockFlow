from InquirerPy import inquirer
from InquirerPy.base import Choice
from i18n import t

from src.core.vars import DATABASE_FOLDER
from src.modules import VIDEO_MODULES



def ask_integer(message: str = "info.interface.ask.integer", **kwargs) -> int:
    """Общая функция для выбора целого числа."""
    return int(inquirer.number(message=f"{t(message)}:", float_allowed=False, **kwargs).execute())

def ask_not_negative_integers(message: str = "info.interface.ask.not_negative_integer", **kwargs) -> int:
    """Общая функция для не отрицательного целого числа."""
    return ask_integer(message=message, min_allowed=0, validate=lambda x: int(x) >= 0, **kwargs)

def ask_amount(message: str = "info.interface.ask.amount", **kwargs) -> int:
    """Общая функция для выбора кол-ва."""
    return ask_not_negative_integers(message=message, **kwargs)

def ask_generation_amount(message: str = "info.interface.ask.generations_amount", **kwargs):
    """Выбор кол-ва генераций."""
    return ask_amount(message=message, **kwargs)



def ask_string(message: str = "info.interface.ask.string", **kwargs) -> str:
    """Общая функция для выбора строки."""
    return inquirer.text(message=f"{t(message)}:", **kwargs).execute()

def ask_new_database(message: str = "info.interface.ask.ask_new_database", **kwargs) -> str:
    return ask_string(message=message, **kwargs)

def ask_conversation_url(message: str = "info.interface.ask.conversation_url.message", long_instructions: str = "info.interface.ask.conversation_url.long", **kwargs) -> str:
    return ask_string(message, long_instructions=long_instructions, **kwargs)

def ask_database(message: str = "info.interface.ask.database", default=None, back=False, **kwargs) -> str:
    """Выбор базы данных."""
    back_message = t("menu.back")
    create_new = t("info.interface.ask.new_database")
    all_databases = [database.stem for database in DATABASE_FOLDER.glob("*.db")]
    choices = all_databases + [create_new]
    if default:
        default = t(default)
    if back:
        choices = [back_message] + choices
    answer = inquirer.select(message=f"{t(message)}:", choices=choices, default=default, **kwargs).execute()
    if answer == create_new:
        return ask_new_database()
    elif answer == back_message:
        raise KeyboardInterrupt
    else:
        return answer


def ask_video_modules(message: str = "info.interface.ask.video_modules", default=None, **kwargs) -> list:
    """Выбор видео модуля"""
    back_message = t("menu.back")
    choices = [Choice(key, enabled=key in default) for key in VIDEO_MODULES.keys()]
    answer = inquirer.checkbox(
        message=f"{t(message)}:",
        choices=choices,
        default=tuple(default),
        **kwargs
    ).execute()
    if answer == back_message:
        raise KeyboardInterrupt
    return answer

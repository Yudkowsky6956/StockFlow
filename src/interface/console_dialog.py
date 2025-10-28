from InquirerPy import inquirer
from i18n import t

from src.core.vars import DATABASE_FOLDER
from src.utils.validators import is_not_negative


def ask_integer(message: str = "info.interface.ask.integer", **kwargs) -> int:
    """Общая функция для выбора целого числа."""
    return inquirer.number(message=f"{t(message)}:", float_allowed=False, **kwargs).execute()

def ask_not_negative_integers(message: str = "info.interface.ask.not_negative_integer", **kwargs) -> int:
    """Общая функция для не отрицательного целого числа."""
    return ask_integer(message=message, min_allowed=0, validator=is_not_negative, **kwargs)

def ask_amount(message: str = "info.interface.ask.amount", **kwargs) -> int:
    """Общая функция для выбора кол-ва."""
    return ask_not_negative_integers(message=message, **kwargs)

def ask_generation_amount(message: str = "info.interface.ask.generations_amount"):
    """Выбор кол-ва генераций."""
    return ask_amount(message=message, initialvalue=1000, minvalue=0)



def ask_string(message: str = "info.interface.ask.string", **kwargs) -> str:
    """Общая функция для выбора строки."""
    return inquirer.text(message=f"{t(message)}:", **kwargs).execute()

def ask_new_database(message: str = "info.interface.ask.ask_new_database", **kwargs) -> str:
    return ask_string(message=message, **kwargs)



def ask_database(message: str = "info.interface.ask.database", default=None, back=None, **kwargs) -> str:
    """Выбор базы данных."""
    back_message = t("menu.back")
    create_new = t("info.interface.ask.new_database")
    all_databases = [database.stem for database in DATABASE_FOLDER.glob("*.db")]
    choices = all_databases + [create_new]
    if default:
        default = t(default)
    if back:
        choices = [back_message] + choices
    answer = inquirer.select(message=t(message), choices=choices, default=default, **kwargs).execute()
    if answer == create_new:
        return ask_new_database()
    elif answer == back_message:
        raise KeyboardInterrupt
    else:
        return answer


def ask_modules(message: str = "info.interface.ask.modules", all_modules=None, back=None)

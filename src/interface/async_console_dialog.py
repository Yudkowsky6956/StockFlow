from InquirerPy import inquirer
from InquirerPy.base import Choice
from i18n import t

from src.core.vars import DATABASE_FOLDER
from src.modules import PHOTO_MODULES, VIDEO_MODULES


# -----------------------------
# ЧИСЛА
# -----------------------------

async def ask_integer(message: str = "info.interface.ask.integer", **kwargs) -> int:
    """Асинхронный выбор целого числа."""
    value = await inquirer.number(
        message=f"{t(message)}:",
        float_allowed=False,
        **kwargs
    ).execute_async()
    return int(value)


async def ask_not_negative_integers(message: str = "info.interface.ask.not_negative_integer", **kwargs) -> int:
    """Асинхронный выбор неотрицательного целого числа."""
    return await ask_integer(
        message=message,
        min_allowed=0,
        validate=lambda x: int(x) >= 0,
        **kwargs
    )


async def ask_amount(message: str = "info.interface.ask.amount", **kwargs) -> int:
    return await ask_not_negative_integers(message=message, **kwargs)


async def ask_generation_amount(message: str = "info.interface.ask.generations_amount", **kwargs):
    return await ask_amount(message=message, **kwargs)


async def ask_float(message: str = "info.interface.ask.float", **kwargs) -> float:
    """Асинхронный выбор float."""
    value = await inquirer.number(
        message=f"{t(message)}:",
        float_allowed=True,
        **kwargs
    ).execute_async()
    return float(value)


async def ask_not_negative_float(message: str = "info.interface.ask.not_negative_float", **kwargs) -> float:
    return await ask_float(
        message=message,
        min_allowed=0,
        validate=lambda x: float(x) >= 0,
        **kwargs
    )


# -----------------------------
# СТРОКИ
# -----------------------------

async def ask_string(message: str = "info.interface.ask.string", **kwargs) -> str:
    """Асинхронный ввод строки."""
    value = await inquirer.text(
        message=f"{t(message)}:",
        **kwargs
    ).execute_async()
    return value


async def ask_new_database(message: str = "info.interface.ask.ask_new_database", **kwargs) -> str:
    return await ask_string(message=message, **kwargs)


async def ask_conversation_url(
    message: str = "info.interface.ask.conversation_url.message",
    long_instructions: str = "info.interface.ask.conversation_url.long",
    **kwargs
) -> str:
    return await ask_string(message, long_instructions=long_instructions, **kwargs)


# -----------------------------
# БАЗА ДАННЫХ
# -----------------------------

async def ask_database_name(message: str = "info.interface.ask.ask_new_database") -> str:
    """Асинхронный ввод имени базы данных."""
    name = await inquirer.text(
        message=f"{t(message)}:"
    ).execute_async()

    return name.strip() if name else None


async def ask_database(message: str = "info.interface.ask.database", default=None, back=False, **kwargs) -> str:
    """Асинхронный выбор базы данных."""
    back_message = t("menu.back")
    create_new = t("info.interface.ask.new_database")

    all_databases = [db.stem for db in DATABASE_FOLDER.glob("*.db")]
    choices = all_databases + [create_new]

    if default:
        default = t(default)

    if back:
        choices = [back_message] + choices

    answer = await inquirer.select(
        message=f"{t(message)}:",
        choices=choices,
        default=default,
        **kwargs
    ).execute_async()

    if answer == create_new:
        return await ask_database_name()

    if answer == back_message:
        raise KeyboardInterrupt

    return answer


# -----------------------------
# МОДУЛИ VIDEO / PHOTO
# -----------------------------

async def ask_video_modules(message: str = "info.interface.ask.video_modules", default=None, **kwargs) -> list:
    back_message = t("menu.back")
    choices = [Choice(key, enabled=key in default) for key in VIDEO_MODULES.keys()]

    answer = await inquirer.checkbox(
        message=f"{t(message)}:",
        choices=choices,
        default=tuple(default),
        **kwargs
    ).execute_async()

    if answer == back_message:
        raise KeyboardInterrupt

    return answer


async def ask_photo_modules(message: str = "info.interface.ask.photo_modules", default=None, **kwargs) -> list:
    back_message = t("menu.back")
    if not default:
        default = []
    choices = [Choice(key, enabled=key in default) for key in PHOTO_MODULES.keys()]

    answer = await inquirer.checkbox(
        message=f"{t(message)}:",
        choices=choices,
        default=tuple(default),
        **kwargs
    ).execute_async()

    if answer == back_message:
        raise KeyboardInterrupt

    return answer


# -----------------------------
# ПРОЧЕЕ
# -----------------------------

async def ask_double(message: str = "info.interface.ask.double_message", **kwargs) -> bool:
    single = t("info.interface.ask.double_false")
    double = t("info.interface.ask.double_true")

    answer = await inquirer.select(
        message=f"{t(message)}:",
        choices=[single, double],
        default=single,
        **kwargs
    ).execute_async()

    return answer == double


async def ask_yes_no(message: str = "info.interface.ask.yes_no_message", **kwargs) -> bool:
    back_message = t("menu.back")
    yes = t("info.interface.ask.yes_answer")
    no = t("info.interface.ask.no_answer")

    answer = await inquirer.select(
        message=f"{t(message)}:",
        choices=[back_message, yes, no],
        **kwargs
    ).execute_async()

    return answer == yes

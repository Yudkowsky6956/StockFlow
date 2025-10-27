from InquirerPy import inquirer
from i18n import t
import texteditor

from src.flows import *
from src.flows.vars import FLOWS_YML
from src.scripts import import_prompts, mark_files_as_done
from src.utils.console import clear_last_lines


BACK = "menu.back"

MAIN_MESSAGE = "menu.main.message"
MAIN_FLOWS = "menu.main.flows"
MAIN_SCRIPTS = "menu.main.scripts"
MAIN_SETTINGS = "menu.main.settings"
MAIN_EXIT = "menu.main.exit"

FLOWS_MESSAGE = "menu.flows.message"
FLOWS_VIDEOS_FROM_PROMPTS = "menu.flows.videos_from_prompts"
FLOWS_VIDEOS_FROM_PHOTOS = "menu.flows.videos_from_photos"

SCRIPTS_MESSAGE = "menu.scripts.message"
SCRIPTS_IMPORT_PROMPTS = "menu.scripts.import_prompts"
SCRIPTS_MARK_FILES_AS_DONE = "menu.scripts.mark_files_as_done"

SETTINGS_MESSAGE = "menu.settings.message"
SETTINGS_GLOBAL = "menu.settings.global"
SETTINGS_FLOWS = "menu.settings.flows"


def menu(message: str, choices_map: dict, default_choice: str | None = None):
    """
    Универсальная функция для меню.

    :param message: Заголовок меню.
    :param choices_map: Словарь {"элемент": функция}.
    :param default_choice: Элемент меню, выбранный по умолчанью.
    :return:
    """
    while True:
        choices = list(choices_map.keys())
        choice = inquirer.select(
            message=f"{t(message)}:",
            choices=choices,
            default=default_choice or choices[0],
        ).execute()
        clear_last_lines(amount=1)

        action = choices_map.get(choice)
        if callable(action):
            action()
        elif action == "back":
            break



def run_main_menu():
    """Запускает главное меню StockFlow"""
    menu(
        message=t(MAIN_MESSAGE),
        choices_map={
            t(MAIN_FLOWS): run_flows_menu,
            t(MAIN_SCRIPTS): run_scripts_menu,
            t(MAIN_SETTINGS): run_settings_menu,
            t(MAIN_EXIT): lambda: exit(0)
        }
    )


def run_flows_menu():
    menu(
        message=t(FLOWS_MESSAGE),
        choices_map={
            t(BACK): "back",
            t(FLOWS_VIDEOS_FROM_PROMPTS): GenerateVideosFromPrompts.run,
            t(FLOWS_VIDEOS_FROM_PHOTOS): GenerateVideosFromPhotos.run
        }
    )


def run_scripts_menu():
    menu(
        message=t(SCRIPTS_MESSAGE),
        choices_map={
            t(BACK): "back",
            t(SCRIPTS_IMPORT_PROMPTS): import_prompts,
            t(SCRIPTS_MARK_FILES_AS_DONE): mark_files_as_done
        }
    )


def run_settings_menu():
    menu(
        message=t(SETTINGS_MESSAGE),
        choices_map={
            t(BACK): "back",
            t(SETTINGS_GLOBAL): "",
            t(SETTINGS_FLOWS): lambda: texteditor.open(filename=FLOWS_YML)
        }
    )


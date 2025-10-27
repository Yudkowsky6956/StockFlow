from InquirerPy import inquirer
from i18n import t

from src.flows.generate_videos import prompts_to_videos
from src.utils.interface import import_prompts, import_hash


def start_menu():
    NAME = t("menu.basic.name")
    FLOWS = t("menu.main.flows")
    SCRIPTS = t("menu.main.scripts")
    SETTINGS = t("menu.main.settings")
    EXIT = t("menu.main.exit")

    while True:
        choice = inquirer.select(
            message=NAME,
            choices=[
                FLOWS,
                SCRIPTS,
                SETTINGS,
                EXIT
            ],
            default=FLOWS,
        ).execute()

        if choice == FLOWS:
            flows_menu()
        elif choice == SCRIPTS:
            scripts_menu()
        elif choice == SETTINGS:
            settings_menu()
        elif choice == EXIT:
            raise SystemExit


def flows_menu():
    FLOWS = t("menu.main.flows")
    GENERATE_VIDEOS = t("menu.flows.generate_videos")
    BACK = t("menu.basic.back")

    while True:
        choice = inquirer.select(
            message=FLOWS,
            choices=[
                BACK,
                GENERATE_VIDEOS
            ],
            default=BACK
        ).execute()

        if choice == BACK:
            start_menu()
        elif choice == GENERATE_VIDEOS:
            prompts_to_videos()


def scripts_menu():
    SCRIPTS = t("menu.main.scripts")
    IMPORT_PROMPTS = t("menu.scripts.import_prompts")
    IMPORT_HASH = t("menu.scripts.import_hash")
    BACK = t("menu.basic.back")

    while True:
        choice = inquirer.select(
            message=SCRIPTS,
            choices=[
                BACK,
                IMPORT_PROMPTS,
                IMPORT_HASH
            ],
            default=IMPORT_PROMPTS
        ).execute()

        if choice == BACK:
            start_menu()
        elif choice == IMPORT_PROMPTS:
            import_prompts()
        elif choice == IMPORT_HASH:
            import_hash()


def settings_menu():
    SCRIPTS = t("menu.main.settings")
    GLOBAL_SETTING = t("menu.settings.global")
    FLOWS_SETTING = t("menu.settings.flows")
    BACK = t("menu.basic.back")

    while True:
        choice = inquirer.select(
            message=SCRIPTS,
            choices=[
                BACK,
                GLOBAL_SETTING,
                FLOWS_SETTING
            ],
            default=BACK
        ).execute()

        if choice == BACK:
            start_menu()
        elif choice == GLOBAL_SETTING:
            pass
        elif choice == FLOWS_SETTING:
            pass


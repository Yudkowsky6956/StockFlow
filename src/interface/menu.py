from .core_menu import Menu
from src.flows import GenerateVideosFromPrompts, GenerateVideosFromPhotos
from src.scripts import import_prompts, mark_files_as_done


class GlobalSettings(Menu):
    GLOBAL_MESSAGE = "menu.global_settings.name"

    name = GLOBAL_MESSAGE
    choices_map = Menu.DEFAULT_CHOICES | {
    }


class FlowSettings(Menu):
    FLOWS_MESSAGE = "menu.flows_settings.name"
    FLOWS_VIDEOS_FROM_PROMPTS = "menu.flows.GenerateVideosFromPrompts"
    FLOWS_VIDEOS_FROM_PHOTOS = "menu.flows.GenerateVideosFromPhotos"

    name = FLOWS_MESSAGE
    choices_map = Menu.DEFAULT_CHOICES | {
        FLOWS_VIDEOS_FROM_PROMPTS: GenerateVideosFromPrompts.run_menu,
        FLOWS_VIDEOS_FROM_PHOTOS: GenerateVideosFromPhotos.run_menu
    }


class SettingsMenu(Menu):
    SETTINGS_MESSAGE = "menu.settings.name"
    SETTINGS_GLOBAL = "menu.settings.global"
    SETTINGS_FLOWS = "menu.settings.flows"

    name = SETTINGS_MESSAGE
    choices_map = Menu.DEFAULT_CHOICES | {
        SETTINGS_GLOBAL: GlobalSettings.run,
        SETTINGS_FLOWS: FlowSettings.run
    }


class FlowsMenu(Menu):
    FLOWS_MESSAGE = "menu.flows.name"
    FLOWS_VIDEOS_FROM_PROMPTS = "menu.flows.GenerateVideosFromPrompts"
    FLOWS_VIDEOS_FROM_PHOTOS = "menu.flows.GenerateVideosFromPhotos"

    name = FLOWS_MESSAGE
    choices_map = Menu.DEFAULT_CHOICES | {
        FLOWS_VIDEOS_FROM_PROMPTS: GenerateVideosFromPrompts.run,
        FLOWS_VIDEOS_FROM_PHOTOS: GenerateVideosFromPhotos.run
    }


class ScriptsMenu(Menu):
    SCRIPTS_MESSAGE = "menu.scripts.name"
    SCRIPTS_IMPORT_PROMPTS = "menu.scripts.import_prompts"
    SCRIPTS_MARK_FILES_AS_DONE = "menu.scripts.mark_files_as_done"

    name = SCRIPTS_MESSAGE
    choices_map = Menu.DEFAULT_CHOICES | {
        SCRIPTS_IMPORT_PROMPTS: import_prompts,
        SCRIPTS_MARK_FILES_AS_DONE: mark_files_as_done
    }


class MainMenu(Menu):
    MAIN_MESSAGE = "menu.main.name"
    MAIN_FLOWS = "menu.main.flows"
    MAIN_SCRIPTS = "menu.main.scripts"
    MAIN_SETTINGS = "menu.main.settings"
    MAIN_EXIT = "menu.main.exit"

    name = MAIN_MESSAGE
    choices_map = {
        MAIN_FLOWS: FlowsMenu.run,
        MAIN_SCRIPTS: ScriptsMenu.run,
        MAIN_SETTINGS: SettingsMenu.run,
        MAIN_EXIT: lambda: exit(0)
    }


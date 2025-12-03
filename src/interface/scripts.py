from i18n import t

from src.scripts import DB_SCRIPTS_LIST, FILES_SCRIPTS_LIST, INFOGRAPHICS_SCRIPTS_LIST
from .core_menu import ConfigurableMenu, Menu


class ScriptsSubMenu(ConfigurableMenu):
    name = "scripts"
    menu_name = "menu_name"

    @classmethod
    def get_item_choice_locale(cls, item):
        return f"config_{cls.name}.{item.__name__}.choice"

    @classmethod
    def get_item_name_locale(cls, item):
        return f"config_{cls.name}.{item.__name__}.name"

    @classmethod
    def get_name(cls):
        return t(f"menu.{cls.menu_name}.name")


class ScriptsInfographics(ScriptsSubMenu):
    menu_name = "infographics_scripts"
    choices = {script: script.run for script in INFOGRAPHICS_SCRIPTS_LIST}

class ScriptsFiles(ScriptsSubMenu):
    menu_name = "files_scripts"
    choices = {script: script.run for script in FILES_SCRIPTS_LIST}

class ScriptsDatabaseMenu(ScriptsSubMenu):
    menu_name = "db_scripts"
    choices = {script: script.run for script in DB_SCRIPTS_LIST}


SCRIPTS_LIST = [ScriptsDatabaseMenu, ScriptsFiles, ScriptsInfographics]


class ScriptsMenu(Menu):
    name = "scripts"
    choices = {menu: menu.run_menu for menu in SCRIPTS_LIST}

    @classmethod
    def get_item_choice_locale(cls, item):
        return f"menu.{item.menu_name}.choice"
from .core_menu import Menu
from src.scripts import DB_SCRIPTS_LIST, FILES_SCRIPTS_LIST, INFOGRAPHICS_SCRIPTS_LIST


class ScriptsSubMenu(Menu):
    @classmethod
    def get_item_choice_locale(cls, item):
        return f"menu.scripts.{item.__name__}.choice"

    @classmethod
    def get_item_name_locale(cls, item):
        return f"menu.scripts.{item.__name__}.name"


class ScriptsInfographics(ScriptsSubMenu):
    name = "infographics_scripts"
    choices = {script: None for script in INFOGRAPHICS_SCRIPTS_LIST}

class ScriptsFiles(ScriptsSubMenu):
    name = "files_scripts"
    choices = {script: None for script in FILES_SCRIPTS_LIST}

class ScriptsDatabaseMenu(ScriptsSubMenu):
    name = "db_scripts"
    choices = {script: None for script in DB_SCRIPTS_LIST}


SCRIPTS_LIST = [ScriptsDatabaseMenu, ScriptsFiles, ScriptsInfographics]


class ScriptsMenu(Menu):
    name = "scripts"
    choices = {menu: menu.run_menu for menu in SCRIPTS_LIST}
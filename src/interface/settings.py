from .core_menu import Menu, ConfigurableMenu
from src.core.settings_mixin import SettingsMixin
from src.core.global_config import GLOBAL_CONFIG_PATH
from ..modules import MODULES_LIST
from ..flows import FLOWS_LIST
from ..scripts import SCRIPTS_LIST


class GlobalSettings(SettingsMixin):
    name = "global"
    menu_config_name = "global"
    CONFIG_PATH = GLOBAL_CONFIG_PATH
    CONFIG_PARAMETERS = ["telegram_account", "notify_account", "notify_on_critical", "notify_on_end"]

class ModulesSettings(ConfigurableMenu):
    name = "modules"
    choices = {module: module.run_menu for module in MODULES_LIST}

class FlowSettings(ConfigurableMenu):
    name = "flows"
    choices = {flow: flow.run_menu for flow in FLOWS_LIST}

class ScriptsSettings(ConfigurableMenu):
    name = "scripts"
    choices = {script: script.run_menu for script in SCRIPTS_LIST}

SETTINGS_LIST = [FlowSettings, ModulesSettings, ScriptsSettings, GlobalSettings]

class SettingsMenu(Menu):
    name = "settings"
    choices = {menu: menu.run_menu for menu in SETTINGS_LIST}
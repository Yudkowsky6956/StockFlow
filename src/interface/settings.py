from .core_menu import Menu, ConfigurableMenu
from ..modules import MODULES_LIST
from ..flows import FLOWS_LIST


class GlobalSettings(ConfigurableMenu):
    name = "global"


class ModulesSettings(ConfigurableMenu):
    name = "modules"
    choices = {module: module.run_menu for module in MODULES_LIST}

class FlowSettings(ConfigurableMenu):
    name = "flows"
    choices = {flow: flow.run_menu for flow in FLOWS_LIST}

SETTINGS_LIST = [FlowSettings, ModulesSettings, GlobalSettings]

class SettingsMenu(Menu):
    name = "settings"
    choices = {menu: menu.run_menu for menu in SETTINGS_LIST}
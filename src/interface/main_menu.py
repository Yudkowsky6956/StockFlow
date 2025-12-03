from .core_menu import Menu
from .flows import FlowsMenu
from .scripts import ScriptsMenu
from .settings import SettingsMenu

MAIN_MENU_LIST = [FlowsMenu, ScriptsMenu, SettingsMenu]

class MainMenu(Menu):
    name = "main"
    choices = {menu: menu.run_menu for menu in MAIN_MENU_LIST}
    SOURCE = True

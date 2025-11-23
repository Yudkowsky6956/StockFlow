from .core_menu import Menu
from .settings import SettingsMenu
from .scripts import ScriptsMenu
from .flows import FlowsMenu


MAIN_MENU_LIST = [FlowsMenu, ScriptsMenu, SettingsMenu]

class MainMenu(Menu):
    name = "main"
    choices = {menu: menu.run_menu for menu in MAIN_MENU_LIST}
    SOURCE = True

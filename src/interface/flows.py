from .core_menu import ConfigurableMenu
from src.flows import FLOWS_LIST


class FlowsMenu(ConfigurableMenu):
    name = "flows"
    choices = {flow: flow.run for flow in FLOWS_LIST}
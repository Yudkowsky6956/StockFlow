from src.flows import FLOWS_LIST
from .core_menu import ConfigurableMenu


class FlowsMenu(ConfigurableMenu):
    name = "flows"
    choices = {flow: flow.run for flow in FLOWS_LIST}
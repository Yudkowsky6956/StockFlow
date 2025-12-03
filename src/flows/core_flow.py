import asyncio

from src.core.settings_mixin import SettingsMixin
from src.core.stop_event import StopEvent
from src.core.syntx.current_module import SyntxCurrentModule
from .vars import FLOWS_YML


class CoreFlow(SettingsMixin):
    menu_config_name = "flows"
    NAME = "flow"
    CONFIG_PATH = FLOWS_YML
    LOCALE_NAME = "config_flow"

    @classmethod
    def run(cls) -> list:
        """
        Синхронная точка входа в сценарий.
        Возвращает список результатов сценария.
        """
        result = asyncio.run(cls._run())
        return result

    @classmethod
    async def _reset_modules(cls, modules):
        SyntxCurrentModule.reset()
        StopEvent.event = asyncio.Event()
        for module in modules:
            await module.init_locks()

    @classmethod
    async def _run(cls) -> list:
        """
        Backend-функция входа в сценарий, которую нужно перегружать в дочерних функциях.

        :return: Список результатов сценария.
        """








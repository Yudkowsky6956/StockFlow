import asyncio

from src.core.settings_mixin import SettingsMixin
from .vars import FLOWS_YML
from ..core.syntx import GenerationError


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
        try:
            tasks = []
            config = cls.get_config()
            result = asyncio.run(cls._run(tasks, config))
            return result
        except GenerationError:
            return []

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        """
        Backend-функция входа в сценарий, которую нужно перегружать в дочерних функциях.

        :param tasks: Список задач сценария.
        :param config: Конфигурация сценария.
        :return: Список результатов сценария.
        """








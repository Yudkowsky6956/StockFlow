import asyncio

import yaml

from src.core.database import Database
from .vars import FLOWS_YML
from .config import FlowConfig


class Flow:
    NAME = "flow"

    @classmethod
    def run(cls) -> list:
        """
        Синхронная точка входа в сценарий.

        :return: Список результатов сценария.
        """
        results = []
        tasks = []
        config = cls.get_config()
        database = FlowConfig.get_database(config)

        return asyncio.run(cls._run(results, tasks, config, database))

    @classmethod
    async def _run(cls, results: list, tasks: list, config: dict, database: Database) -> list:
        """
        Backend-функция входа в сценарий, которую нужно перегружать в дочерних функциях.

        :param results: Список результатов сценария.
        :param tasks: Список задач сценария.
        :param config: Конфигурация сценария.
        :param database: База данных сценария.
        :return: Список результатов сценария.
        """

    @classmethod
    def get_config(cls) -> dict:
        """
        Загружает конфиг для данного сценария.

        :return: Словарь конфига сценария.
        """
        return yaml.safe_load(FLOWS_YML.read_text(encoding="utf-8"))[cls.__name__]






from pathlib import Path
from src.core.database import Database
from src.interface.select import (
    select_video_folder,
    select_photo_folder,
    select_generation_amount,
    select_database,
)


class FlowConfig:
    """
    Класс для получения параметров сценария из конфигурации.
    Если параметр отсутствует — вызывается соответствующий диалог выбора.
    """
    # @classmethod
    # def get_video_folder(cls, config: dict) -> Path:
    #     """
    #     Загружает путь к папке для видео.
    #
    #     :param config: Конфигурация сценария.
    #     :return: Путь к папке с видео.
    #     """
    #     folder = config.get("video_folder")
    #     if not folder:
    #         folder = select_video_folder()
    #     return Path(folder)
    #
    # @classmethod
    # def get_photo_folder(cls, config: dict) -> Path:
    #     """
    #     Загружает путь к папке для фотографий.
    #
    #     :param config: Конфигурация сценария.
    #     :return: Путь к папке с фотографиями.
    #     """
    #     folder = config.get("photo_folder")
    #     if not folder:
    #         folder = select_photo_folder()
    #     return Path(folder)

    @classmethod
    def get_generations_amount(cls, config: dict) -> int:
        """
        Загружает количество генераций.

        :param config: Конфигурация сценария.
        :return: Количество генераций.
        """
        amount = config.get("amount")
        if not amount:
            amount = select_generation_amount()
        return int(amount)

    @classmethod
    def get_database(cls, config: dict) -> Database:
        """
        Загружает базу данных.

        :param config: Конфигурация сценария.
        :return: База данных.
        """
        database = config.get("database")
        if not database:
            database = select_database()
        return Database(database)

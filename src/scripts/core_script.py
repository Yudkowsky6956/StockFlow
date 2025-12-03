import asyncio

from i18n import t

from src.core.logger import logger
from src.core.settings_mixin import SettingsMixin
from .vars import SCRIPTS_YML


class CoreScript(SettingsMixin):
    starting_script = t("info.scripts.starting_script")
    menu_config_name = "scripts"
    CONFIG_PATH = SCRIPTS_YML

    @classmethod
    def run(cls):
        """Синхронная точка входа в скрипт"""
        logger.success(f"{cls.starting_script}: {t(f"scripts.{cls.__name__}.name")}")
        return asyncio.run(cls._run())

    @classmethod
    async def _run(cls):
        """Бэк-функция входа в скрипт, которую нужно перегружать"""


class ScriptsDB(CoreScript):
    pass

class FilesScripts(CoreScript):
    pass

class InfographicsScripts(CoreScript):
    pass


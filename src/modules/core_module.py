import asyncio

from i18n import t
from loguru import logger as default_logger
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from src.core.database import Database
from src.core.pyrogram.filters import contains
from src.core.settings_mixin import SettingsMixin
from src.core.syntx.current_module import SyntxCurrentModule
from src.core.syntx.event_lock import EventLock
from src.core.syntx.exceptions import GenerationError
from src.modules.vars import *


class CoreModule(SettingsMixin):
    CONFIG_PARAMETERS = ["name", "color", "timeout", "batch_size"]
    menu_config_name = "modules"
    event_lock = None
    syntx_lock = None
    semaphore = None
    CONFIG_PATH = MODULES_YML
    LOCALE_NAME = "config_module"
    output_amount = 1

    @classmethod
    async def _generate(cls, *args, **kwargs) -> Message:
        pass

    @classmethod
    async def _run(cls, *args, **kwargs):
        pass

    @classmethod
    def get_semaphore(cls):
        config = cls.get_config()
        if not cls.semaphore:
            cls.semaphore = asyncio.Semaphore(config.get("batch_size", 1))
        return cls.semaphore

    @classmethod
    def get_name(cls):
        return cls.get_config().get("name", "TEMPLATE")

    @classmethod
    def get_color(cls):
        return cls.get_config().get("color", "#FFFFFF")

    @classmethod
    def get_timeout(cls):
        return cls.get_config().get("timeout", 3600)

    @classmethod
    def get_batch_size(cls):
        return cls.get_config().get("batch_size", 1)


class SyntxModule(CoreModule):
    menu_message = MENU_MESSAGE
    menu_response = MENU_RESPONSE
    _bot = None

    @classmethod
    def set_bot(cls, bot: "SyntxBot"):
        cls._bot = bot

    @classmethod
    def bot(cls) -> "SyntxBot":
        if not cls._bot:
            raise RuntimeError("You can't use SyntxModule without bot. Please call \"set_bot\"")
        return cls._bot

    @classmethod
    async def init_locks(cls):
        config = cls.get_config()
        cls.semaphore = asyncio.Semaphore(config.get("batch_size", 1))
        cls.syntx_lock = asyncio.Lock()
        cls.event_lock = EventLock()

    @classmethod
    async def _handle_generation_error(cls, e: GenerationError, name: str, database: Database,  logger, mark=True, *args, **kwargs):
        if e.log and not e.fatal:
            logger.error(t(e.log), delay=e.delay)

        if e.mark:
            database.mark_error(name)

        if e.lock and e.delay:
            cls.event_lock.turn_on()

        if e.delay:
            await asyncio.sleep(e.delay)
            if e.lock:
                cls.event_lock.turn_off()
            return await cls.run(name, logger, database, mark, *args, **kwargs)

        if e.fatal:
            raise e

    @classmethod
    async def run_back(cls, name: str, database: Database, logger, mark=True, *args, **kwargs):
        config = cls.get_config()
        if mark and database.is_done(name, config["name"]):
            raise GenerationError(f"Skips generation of {name}")

        logger = logger.bind(module_name=config["name"], module_color=config["color"])
        result = await cls._run(name=name, logger=logger, database=database, *args, **kwargs)
        if mark:
            database.mark_done(name, config["name"])
        return result

    @classmethod
    async def run(cls, name: str, logger, database: Database, mark=True, *args, **kwargs):
        config = cls.get_config()
        try:
            try:
                async with cls.get_semaphore():
                    await cls.event_lock.wait()
                    result = await asyncio.wait_for(
                        cls.run_back(
                            name,
                            database,
                            logger.bind(module_name=config["name"], module_color=config["color"]),
                            mark,
                            *args,
                            **kwargs
                        ),
                        timeout=config["timeout"]
                    )
                    return result
            except asyncio.TimeoutError:
                log_message = t("error.timeout_error")
                raise GenerationError(log_message, log=log_message, delay=5)
            except FloodWait as e:
                log_message = t("error.flood_wait").format(delay=e.value)
                raise GenerationError(log_message, log=log_message, delay=e.value, lock=True)
        except GenerationError as e:
            return await cls._handle_generation_error(e, name, database, logger, mark, *args, **kwargs)


    @classmethod
    async def get_button_url(cls, message: Message, button_text: str) -> str:
        if message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if button.text:
                        if button.text == button_text:
                            if button.web_app:
                                if button.web_app.url:
                                    return button.web_app.url
        raise RuntimeError

class CategoryModule(SyntxModule):
    category_message = "MESSAGE"
    category_response = "RESPONSE"

    @classmethod
    async def start(cls):
        """Prepare SyntxAI for Module using async Lock"""
        config = cls.get_config()
        if await SyntxCurrentModule.get() != config["name"]:
            default_logger.debug(f"Switching SyntxAI Module to {config["name"]}")
            await cls._start()

    @classmethod
    async def _start(cls):
        """Prepare SyntxAI for Module"""
        config = cls.get_config()
        await SyntxCurrentModule.set(config["name"])
        user_main_menu_message = await cls.bot().send(cls.menu_message)
        main_menu_message = await cls.bot().wait_for(message=user_main_menu_message, flt=contains(cls.menu_response))
        await cls.bot().delete(main_menu_message)
        user_category_message = await cls.bot().send(cls.category_message)
        category_message = await cls.bot().wait_for(message=user_category_message, flt=contains(cls.category_response))
        await cls.bot().delete(category_message)


class AgentModule(CategoryModule):
    agent_message = "MESSAGE"
    agent_response = "RESPONSE"

    @classmethod
    async def _start(cls):
        """Prepare SyntxAI for Module"""
        await super()._start()
        user_module_message = await cls.bot().send(text=cls.agent_message)
        module_message = await cls.bot().wait_for(message=user_module_message, flt=contains(cls.agent_response))
        await cls.bot().delete(module_message)

class GPTModule(CategoryModule):
    category_message = GPT_MESSAGE
    category_response = GPT_RESPONSE

class DesignModule(AgentModule):
    category_message = DESIGN_MESSAGE
    category_response = DESIGN_RESPONSE

class AudioModule(AgentModule):
    category_message = AUDIO_MESSAGE
    category_response = AUDIO_RESPONSE






import asyncio

from i18n import t
from loguru import logger as default_logger
from pyrogram.types import Message

from src.core.pyrogram.filters import contains
from src.core.database import Database
from .exceptions import GenerationError
from .current_module import SyntxCurrentModule
from .vars import *
from .event_lock import EventLock


class Module:
    pass


class SyntxModule(Module):
    syntx_name = "NAME"
    color = "#FFFFFF"
    semaphore: asyncio.Semaphore = asyncio.Semaphore(1)
    event_lock: EventLock = EventLock()
    syntx_lock = asyncio.Lock()
    menu_message = MENU_MESSAGE
    menu_response = MENU_RESPONSE
    timeout = 60 * 10
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
    async def _generate(cls, *args, **kwargs) -> Message:
        pass

    @classmethod
    async def _run(cls, *args, **kwargs):
        pass

    @classmethod
    async def _handle_generation_error(cls, e: GenerationError, name: str, database: Database,  logger, *args, **kwargs):
        if e.log:
            logger.error(t(e.log, delay=e.delay))

        if e.mark:
            database.mark_error(name)
            pass

        if e.lock and e.delay:
            cls.event_lock.turn_on()

        if e.delay:
            await asyncio.sleep(e.delay)
            if e.lock:
                cls.event_lock.turn_off()
            return await cls.run(name, logger, database, *args, **kwargs)

        if e.fatal:
            raise

    @classmethod
    async def run_back(cls, name: str, database: Database, logger, *args, **kwargs):
        if database.is_done(name, cls.syntx_name):
            raise GenerationError(f"Skips generation of {name}")

        logger = logger.bind(module_name=cls.syntx_name, module_color=cls.color)
        result = await cls._run(name, logger, *args, **kwargs)
        database.mark_done(name, cls.syntx_name)
        return result

    @classmethod
    async def run(cls, name: str, logger, database: Database, *args, **kwargs):
        try:
            try:
                async with cls.semaphore:
                    await cls.event_lock.wait()
                    result = await asyncio.wait_for(
                        cls._run(name, logger.bind(module_name=cls.syntx_name, module_color=cls.color), *args,
                                 **kwargs),
                        timeout=cls.timeout
                    )
                    database.mark_done(name, cls.syntx_name)
                    return result
            except asyncio.TimeoutError:
                raise GenerationError("error.timeout_error", log="error.timeout_error", mark=True)
        except GenerationError as e:
            return await cls._handle_generation_error(e, name, database, logger, *args, **kwargs)


class CategoryModule(SyntxModule):
    category_message = "MESSAGE"
    category_response = "RESPONSE"

    @classmethod
    async def start(cls):
        """Prepare SyntxAI for Module using async Lock"""
        if await SyntxCurrentModule.get() != cls.syntx_name:
            default_logger.debug(f"Switching SyntxAI Module to {cls.syntx_name}")
            await cls._start()

    @classmethod
    async def _start(cls):
        """Prepare SyntxAI for Module"""
        await SyntxCurrentModule.set(cls.syntx_name)
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
    syntx_name = GPT_NAME
    category_message = GPT_MESSAGE
    category_response = GPT_RESPONSE

class DesignModule(AgentModule):
    category_message = DESIGN_MESSAGE
    category_response = DESIGN_RESPONSE

class AudioModule(AgentModule):
    category_message = AUDIO_MESSAGE
    category_response = AUDIO_RESPONSE






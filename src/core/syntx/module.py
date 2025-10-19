import asyncio

from i18n import t
from loguru import logger as default_logger
from prefect import task
from prefect.cache_policies import NO_CACHE
from pyrogram.types import Message

from src.core.pyrogram.filters import contains
from .exceptions import GenerationError
from .asyncio import SyntxCurrentModule
from .vars import *


class Module:
    pass


class SyntxModule(Module):
    syntx_name = "NAME"
    semaphore: asyncio.Semaphore = asyncio.Semaphore(1)
    syntx_lock = asyncio.Lock()
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
    async def _generate(cls, *args, **kwargs) -> Message:
        pass

    @classmethod
    @task(cache_policy=NO_CACHE)
    async def generate(cls, *args, logger=default_logger, **kwargs):
        try:
            logger = logger.bind(module=cls.__name__)
            async with cls.semaphore:
                return await cls._generate(*args, logger=logger, **kwargs)

        except GenerationError as e:
            if e.log:
                logger.error(t(e.log), e.delay)

            if e.mark:
                # TODO: Сделать маркировку запросов
                pass

            if e.delay:
                await asyncio.sleep(e.delay)
                return await cls.generate(*args, logger=logger, **kwargs)

            if e.fatal:
                raise


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






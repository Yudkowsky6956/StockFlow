import asyncio

from loguru import logger

from src.core.pyrogram.filters import contains
from .asyncio import SyntxCurrentModule
from .vars import *


class Module:
    pass


class SyntxModule(Module):
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


class CategoryModule(SyntxModule):
    category_name = "NAME"
    category_message = "MESSAGE"
    category_response = "RESPONSE"

    @classmethod
    async def start(cls):
        """Prepare SyntxAI for Module using async Lock"""
        if await SyntxCurrentModule.get() != cls.category_name:
            logger.debug(f"Switching SyntxAI Module to {cls.category_name}")
            await cls._start()

    @classmethod
    async def _start(cls):
        """Prepare SyntxAI for Module"""
        await SyntxCurrentModule.set(cls.category_name)
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


class DesignModule(AgentModule):
    category_name = DESIGN_NAME
    category_message = DESIGN_MESSAGE
    category_response = DESIGN_RESPONSE


class GPTModule(CategoryModule):
    category_name = GPT_NAME
    category_message = GPT_MESSAGE
    category_response = GPT_RESPONSE


class AudioModule(CategoryModule):
    category_name = AUDIO_NAME
    category_message = AUDIO_MESSAGE
    category_response = AUDIO_RESPONSE






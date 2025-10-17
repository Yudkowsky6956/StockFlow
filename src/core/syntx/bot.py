import asyncio
from typing import List, Optional

from loguru import logger as default_logger
from pyrogram import Client
from pyrogram.filters import AndFilter
from pyrogram.types import Message

from .module import SyntxModule
from src.core.pyrogram.bot import TelegramBot
from src.core.pyrogram.filters import contains, is_replying_to
from .errors import ALL_ERRORS, HandlerError
from .exceptions import GenerationError


class SyntxBot(TelegramBot):
    """Class that represents SyntxAI bot"""

    name = "SyntxAI"
    id = "syntxaibot"

    def __init__(self, client: Client):
        super().__init__(client)
        SyntxModule.set_bot(self)

    async def wait_for(self, flt: AndFilter, message: Optional[Message] = None, send: bool = True, edit: bool = True, reply: bool = False, logger=default_logger) -> Message:
        future = await super().wait_for_future(flt, message, send, edit, reply, logger)
        await self.add_error_handlers(message, future, [], logger)
        return await future

    async def add_error_handlers(self, original_message: Message, future, local_handlers: List, logger=default_logger):
        def _make_handler(err: HandlerError):
            async def handler(_, message):
                for h in local_handlers:
                    await self.remove_handler(h)
                if not future.done():
                    if err.log:
                        if err.fatal:
                            logger.critical(err.log)
                    future.set_exception(GenerationError(message.text, log=err.log, delay=err.delay, fatal=err.fatal, mark=err.mark))
            return handler

        for err in ALL_ERRORS:
            if err.reply:
                method = self.edited_message_handler
                flt = contains(err.message) & is_replying_to(original_message)
            else:
                method = self.message_handler
                flt = contains(err.message)
            local_handlers.append(method(_make_handler(err), flt))

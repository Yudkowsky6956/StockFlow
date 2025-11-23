from typing import List, Optional
import asyncio

from loguru import logger as default_logger
from pyrogram.filters import AndFilter
from pyrogram.types import Message
from i18n import t

from src.modules.core_module import SyntxModule
from src.core.pyrogram.session import Session
from src.core.pyrogram.bot import TelegramBot
from src.core.pyrogram.filters import contains, is_replying_to, message_exists
from .errors import ALL_ERRORS, HandlerError
from .exceptions import GenerationError


class SyntxBot(TelegramBot):
    """Class that represents SyntxAI bot"""

    name = "SyntxAI"
    id = "syntxaibot"

    def __init__(self, session: Session = None, phone_number: str = None):
        super().__init__(session, phone_number)
        SyntxModule.set_bot(self)

    async def wait_for(self, flt: AndFilter, message: Optional[Message] = None, send: bool = True, edit: bool = True, reply: bool = False, logger=default_logger, future=None, request_message=None, photo=None, button_map=None, wait=True) -> Message:
        local_handlers = []
        if not future:
            future = asyncio.get_event_loop().create_future()
        await self.add_error_handlers(message, future, local_handlers, logger, request_message)
        if wait:
            future = await super().wait_for_future(flt, message, send, edit, reply, logger, future, local_handlers, photo, button_map)
            return await future
        else:
            return future

    async def add_error_handlers(self, original_message: Message, future, local_handlers: List, logger=default_logger, request_message=None):
        def _make_handler(error: HandlerError):
            async def handler(_, message):
                for h in local_handlers:
                    await self.remove_handler(h)
                if not future.done():
                    if error.log:
                        if error.fatal:
                            logger.critical(t(error.log))
                    future.set_exception(GenerationError(message.text, log=error.log, delay=error.delay, fatal=error.fatal, mark=error.mark, lock=error.lock))
            return handler

        for err in ALL_ERRORS:
            if err.reply:
                method = self.message_handler
                method_edited = self.edited_message_handler
                flt = contains(err.message) & is_replying_to(original_message)
            else:
                method = self.message_handler
                method_edited = self.edited_message_handler
                flt = contains(err.message)
                if request_message:
                    flt = flt & ~message_exists(request_message)
            local_handlers.append(method(_make_handler(err), flt))
            local_handlers.append(method_edited(_make_handler(err), flt))

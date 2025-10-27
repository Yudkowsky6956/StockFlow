import asyncio
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger as default_logger
from pyrogram import Client, filters, handlers
from src.core.pyrogram.session import Session
from pyrogram.enums import ParseMode
from pyrogram.types import ChatEventFilter, InputMediaPhoto, Message

from src.utils.sentances import wrap_by_words
from .filters import is_replying_to


class TelegramBot:
    """Class which can be used to interact with the Telegram bot"""

    name = ""
    id = ""

    def __init__(self, session: Session = None, phone_number: str = None):
        default_logger.debug(f"Initializing TelegramBot with id = \"{self.id}\".")
        self._handlers = []

        if not session:
            session = Session(phone_number=phone_number)
        self.session = session
        self.client = self.session.client

    def _add_handler(self, func, handler_cls, handler_filter=all):
        handler_filter = filters.chat(self.id) & handler_filter
        handler = handler_cls(func, handler_filter)
        self.client.add_handler(handler)
        self._handlers.append(handler)
        return handler

    def on_message(self, filter_: ChatEventFilter = filters.all):
        """Decorator that replaces Pyrogram _on_message"""
        def decorator(func):
            return self._add_handler(func, handlers.MessageHandler, filter_)
        return decorator

    def on_edited_message(self, filter_: ChatEventFilter = filters.all):
        """Decorator that replaces Pyrogram _on_message for edited messages"""
        def decorator(func):
            return self._add_handler(func, handlers.EditedMessageHandler, filter_)
        return decorator

    def message_handler(self, func, filter_: ChatEventFilter = filters.all):
        """Registers a MessageHandler for new messages"""
        return self._add_handler(func, handlers.MessageHandler, filter_)

    def edited_message_handler(self, func, filter_: ChatEventFilter = filters.all):
        """Registers an EditedMessageHandler for edited messages"""
        return self._add_handler(func, handlers.EditedMessageHandler, filter_)

    @staticmethod
    def _compose_log(text: Optional[str] = None, photo: Optional[Union[Path, List[Path]]] = None, shorten: bool = True):
        photo_text = ""
        if photo:
            if isinstance(photo, Path):
                photo_text = photo.name
            elif isinstance(photo, list):
                photo_text = ", ".join([_photo.name for _photo in photo.copy()])
        if text:
            if shorten:
                text = wrap_by_words(text, 25, "…")
            if isinstance(photo, list):
                return f"text: \"{text}\", photos ({len(photo)}): \"{photo_text}\""
            elif isinstance(photo, Path):
                return f"text: \"{text}\", photo: \"{photo_text}\""
            else:
                return f"text: \"{text}\""
        else:
            if isinstance(photo, list):
                return f"photos ({len(photo)}): \"{photo_text}\""
            elif isinstance(photo, Path):
                return f"photo: \"{photo_text}\""
            return "message"

    async def remove_handler(self, handler):
        """Removes Handler from Pyrogram and local memory"""
        self.client.remove_handler(handler)
        self._handlers.remove(handler)

    async def send(self, text: Optional[str] = None, photo: Optional[Union[Path, List[Path]]] = None, parse_mode=ParseMode.DISABLED, logger=default_logger) -> Message:
        """Sends text and/or image and returns Message"""
        if not text and not photo:
            pass

        if isinstance(photo, list):
            return await self.send_photos(photo, text, parse_mode, logger)
        elif isinstance(photo, Path):
            return await self.send_photo(photo, text, parse_mode, logger)
        else:
            return await self.send_text(text, parse_mode, logger)

    async def send_photos(self, photos: List[Path], text: Optional[str] = None, parse_mode=ParseMode.DISABLED, logger=default_logger) -> Message:
        """Sends photos and optional text and returns message"""
        media = self.compose_media(photos, text, parse_mode)
        logger.debug(f"Sending message with {self._compose_log(text, photos)}.")
        return (await self.client.send_media_group(self.id, media=media))[0]

    async def send_photo(self, photo: Path, text: Optional[str] = None, parse_mode=ParseMode.DISABLED, logger=default_logger) -> Message:
        """Sends photo and optional text and returns message"""
        logger.debug(f"Sending message with {self._compose_log(text, photo)}.")
        return await self.client.send_photo(self.id, str(photo), caption=text, parse_mode=parse_mode)

    async def send_text(self, text: str, parse_mode=ParseMode.DISABLED, logger=default_logger) -> Message:
        """Sends text and returns message"""
        logger.debug(f"Sending message with {self._compose_log(text, None)}.")
        return await self.client.send_message(self.id, text, parse_mode=parse_mode)

    @classmethod
    def compose_media(cls, photos: List[Path], text: Optional[str] = None, parse_mode=ParseMode.DISABLED) -> List[InputMediaPhoto]:
        """Composes photos and optional text and returns media group"""
        media = []
        for index, photo in enumerate(photos):
            if index == 0:
                media.append(InputMediaPhoto(str(photo), caption=text, parse_mode=parse_mode))
            else:
                media.append(InputMediaPhoto(str(photo)))
        return media

    async def wait_for_future(self, flt, message: Optional[Message] = None, send=True, edit=True, reply=False, logger=default_logger, future=None, local_handlers=None) -> asyncio.Future:
        """Waits for Filter message to arrive/edit and returns future"""
        logger.debug(f"Waiting response for {self._compose_log(message.text or message.caption, None)}.")
        if not future:
            future = asyncio.get_event_loop().create_future()
        if not local_handlers:
            local_handlers = []

        async def _finish_wait(_, message):
            """Finishes the wait_for function"""
            for h in local_handlers:
                await self.remove_handler(h)
            logger.debug(f"The response obtained for {self._compose_log(message.text or message.caption, None)}.")
            if not future.done():
                future.set_result(message)
            return message

        if reply:
            flt = flt & is_replying_to(message)
        if send:
            local_handlers.append(self.message_handler(_finish_wait, flt))
        if edit:
            local_handlers.append(self.edited_message_handler(_finish_wait, flt))
        return future

    async def wait_for(self, flt, message: Optional[Message] = None, send=True, edit=True, reply=False, logger=default_logger, future=None) -> Message:
        """Waits for Filter message to arrive/edit and returns message"""
        if not future:
            future = asyncio.get_event_loop().create_future()
        future = await self.wait_for_future(flt, message, send, edit, reply, logger, future)
        return await future

    async def delete(self, message: Message, logger=default_logger):
        """Deletes a Message"""
        logger.debug(f"Deleting message with {self._compose_log(message.text or message.caption, None)}")
        await self.client.delete_messages(self.id, message.id)

    async def download(self, message: Message, path: Path, logger=default_logger) -> Path:
        """Downloads file from Message and returns Path"""
        if message.media:
            logger.debug(f"Downloading media from message with {self._compose_log(message.text or message.caption, None)}.")
            return Path(await message.download(str(path), in_memory=False))
        raise RuntimeError(f"Provided message with {self._compose_log(message.text or message.caption, None)} hasn't media to download.")
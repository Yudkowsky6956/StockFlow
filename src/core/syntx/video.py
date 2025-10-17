from pyrogram.types import Message
from loguru import logger as default_logger

from typing import Optional, Union, List
from pathlib import Path

from .vars import VIDEO_IMAGE_RESPONSE, YOUR_REQUEST, VIDEO_NAME, VIDEO_MESSAGE, VIDEO_RESPONSE
from .module import AgentModule
from src.core.pyrogram.filters import contains


class VideoModule(AgentModule):
    max_photos_per_batch = 1

    category_name = VIDEO_NAME
    category_message = VIDEO_MESSAGE
    category_response = VIDEO_RESPONSE

    @classmethod
    async def load_photos(cls, photos: List[Path], logger=default_logger):
        photos = photos[:cls.max_photos_per_batch]
        for index, photo in enumerate(photos, start=1):
            await cls.load_photo(photo, index, logger)

    @classmethod
    async def load_photo(cls, photo: Path, index: int, logger=default_logger):
        image_loaded_message = await cls.bot().send(photo=photo, logger=logger)
        await cls.bot().wait_for(
            message=image_loaded_message,
            flt=contains(VIDEO_IMAGE_RESPONSE.format(index)),
            replying=True,
            logger=logger
        )


class VideoInBot(VideoModule):
    @classmethod
    async def generate(cls, prompt: str, photo: Optional[Union[Path, List[Path]]] = None, logger=default_logger) -> Message:
        async with cls.syntx_lock:
            await cls.start()
            logger.info("Generating video...")
            if photo:
                await cls.load_photos(photo, logger)
            prompt_message = await cls.bot().send(text=prompt)
        return await cls.bot().wait_for(
            message=prompt_message,
            flt=contains(YOUR_REQUEST.format(prompt[:50])),
            logger=logger
        )
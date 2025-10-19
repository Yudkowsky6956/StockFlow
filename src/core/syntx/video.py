from pathlib import Path
from typing import List, Optional, Union, Tuple

from i18n import t
from playwright.async_api import async_playwright
from loguru import logger as default_logger
from pyrogram.types import Message

from src.core.pyrogram.filters import contains
from .module import AgentModule
from .vars import VIDEO_IMAGE_RESPONSE, VIDEO_MESSAGE, VIDEO_NAME, VIDEO_RESPONSE, YOUR_REQUEST, VIDEO_URL_BUTTON, VIDEO_IMAGE_RESPONSE_ONE
from ...modules.vars import EMPTY_PROMPT


class VideoModule(AgentModule):
    max_photos_per_batch = 1

    category_name = VIDEO_NAME
    category_message = VIDEO_MESSAGE
    category_response = VIDEO_RESPONSE

    @classmethod
    async def load_photos(cls, photos: Union[Path, List[Path]], logger=default_logger) -> Tuple[Message, Message]:
        message = None
        input_message = None
        if isinstance(photos, Path):
            photos = [photos]
        elif isinstance(photos, list):
            photos = photos[:cls.max_photos_per_batch]
        logger.info(t(f"info.video.loading_photos"), amount=len(photos))
        for index, photo in enumerate(photos, start=1):
            message, input_message = await cls.load_photo(photo, index, logger)
        return message, input_message

    @classmethod
    async def load_photo(cls, photo: Path, index: int, logger=default_logger) -> Tuple[Message, Message]:
        flt = contains(VIDEO_IMAGE_RESPONSE.format(index))
        if index == 1:
            flt = flt | contains(VIDEO_IMAGE_RESPONSE_ONE)
        image_loaded_message = await cls.bot().send(photo=photo, logger=logger)
        answer_message = await cls.bot().wait_for(
            message=image_loaded_message,
            flt=flt,
            reply=True,
            logger=logger
        )
        return answer_message, image_loaded_message


class VideoInBot(VideoModule):
    @classmethod
    async def _generate(cls, prompt: str, photo: Optional[Union[Path, List[Path]]] = None, logger=default_logger) -> Message:
        async with cls.syntx_lock:
            await cls.start()
            if photo:
                await cls.load_photos(photo, logger)
            prompt_message = await cls.bot().send(text=prompt, logger=logger)
        logger.info(t("info.video.generating"))
        message = await cls.bot().wait_for(
            message=prompt_message,
            flt=contains(YOUR_REQUEST.format(prompt[:50])),
            logger=logger
        )
        logger.info(t("info.video.generation_end"))
        return message


class VideoMiniApp(VideoModule):
    @classmethod
    async def get_generate_button(cls, message: Message) -> str:
        if message.reply_markup:
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if button.text:
                        if button.text == VIDEO_URL_BUTTON:
                            if button.web_app:
                                if button.web_app.url:
                                    return button.web_app.url
        raise RuntimeError

    @classmethod
    async def _generate_from_photo(cls, message: Message, prompt: Optional[str] = None, logger=default_logger):
        url = await cls.get_generate_button(message)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url)
            if prompt:
                prompt_input = await page.query_selector("#prompt")
                await prompt_input.click()
                await prompt_input.fill(prompt)
            submit_button = await page.query_selector("#crop")
            await submit_button.click()

    @classmethod
    async def _generate(cls, prompt: Optional[str] = None, photo: Optional[Union[Path, List[Path]]] = None, logger=default_logger) -> Message:
        if not prompt:
            prompt = EMPTY_PROMPT
        async with cls.syntx_lock:
            await cls.start()
            if photo:
                start_generation_message, photo_message = await cls.load_photos(photo, logger)
                await cls._generate_from_photo(start_generation_message, prompt, logger)
            logger.info(t("info.video.generating"))
            message = await cls.bot().wait_for(
                message=photo_message,
                flt=contains(YOUR_REQUEST.format(prompt[:50])),
                logger=logger
            )
            logger.info(t("info.video.generation_end"))
            return message



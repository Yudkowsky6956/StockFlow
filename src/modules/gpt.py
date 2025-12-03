import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from i18n import t

from src.core.pyrogram.filters import has_inline_button
from src.core.syntx.exceptions import GenerationError
from src.modules.core_module import CategoryModule
from src.modules.vars import GPT_MESSAGE, GPT_RESPONSE, GPT_VIEW_FULL_DIALOG
from src.utils.sentances import compile_prompt


class GPTModule(CategoryModule):
    category_message = GPT_MESSAGE
    category_response = GPT_RESPONSE

    URL_CHECK_FLAG = False
    last_send_time: float = 0
    send_delay: float = 6.0


    @classmethod
    async def _generate(cls, prompt: str, logger, photo: Path | list[Path] | None = None):
        async with cls.syntx_lock:
            await cls.start()
            # now = asyncio.get_event_loop().time()
            # wait_time = cls.last_send_time + cls.send_delay - now
            # if wait_time > 0:
            #     await asyncio.sleep(wait_time)
            prompt_message = await cls.bot().send(text=prompt, logger=logger, photo=photo)
            # cls.last_send_time = asyncio.get_event_loop().time()
            after_time = cls.get_time()
            gpt_task = asyncio.create_task(cls.bot().wait_for(
                flt=has_inline_button(GPT_VIEW_FULL_DIALOG),
                message=prompt_message,
                reply=True
            ))
            logger.info(t("info.gpt.generating"))
            await asyncio.sleep(6)
        message = await gpt_task
        url = await cls.get_button_url(message, GPT_VIEW_FULL_DIALOG)
        message_text = await cls.get_answer_text(prompt_message, after_time, url)
        logger.info(t("info.gpt.generation_end"))
        return message_text

    @classmethod
    async def _run(cls, name: str, logger, prompt: str, database, photo: Path | list[Path] | None = None):
        prompt = compile_prompt(name, prompt)
        return await cls._generate(prompt=prompt, photo=photo, logger=logger)

    @staticmethod
    def get_time():
        tz = timezone(timedelta(hours=3))
        return datetime.now(tz) - timedelta(seconds=3)

    @staticmethod
    async def get_soup(url: str):
        headers = {"Range": "bytes=-2000"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                text = await response.text()
        return BeautifulSoup(text, "html.parser")

    @staticmethod
    async def get_answer_text(message, after_time, url):
        text = message.text or message.caption
        soup = await GPTModule.get_soup(url)
        questions = soup.find_all("div", class_="message userquestion")[-25:]

        for q in questions:
            for btn in q.find_all("button", class_="copy-message-button"):
                btn.decompose()
            q_text = q.get_text(strip=True)

            if text not in q_text:
                continue

            time_tag = q.find("i", class_="bi-clock-history")
            if time_tag and time_tag.next_sibling:
                time_str = time_tag.next_sibling.strip()
                try:
                    msg_dt = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S GMT%z")
                except ValueError:
                    continue

                if after_time and msg_dt < after_time:
                    continue

            answer_block = q.find_next("div", class_="message answer")
            if not answer_block:
                continue

            json_code = answer_block.find("code", class_="language-json")
            if not json_code:
                continue

            json_text = json_code.get_text(strip=True)
            return json.loads(json_text)

        raise GenerationError(
            t("error.wrong_conversation_id"),
            fatal=True
        )






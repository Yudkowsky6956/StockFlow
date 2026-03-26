import asyncio
import json
import tempfile
from datetime import datetime, timedelta, timezone
from json.decoder import JSONDecodeError
from pathlib import Path

import os
import aiohttp
import openai
import requests
from PIL import Image
from bs4 import BeautifulSoup
from i18n import t
import base64
from loguru import logger
from openai import AsyncOpenAI
import re

from src.core.pyrogram.filters import has_inline_button
from src.core.syntx import locks
from src.core.syntx.exceptions import GenerationError
from src.modules.core_module import CategoryModule, SyntxModule
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
        async with locks.locks["syntx_lock"]:
            await cls.start()
            # now = asyncio.get_event_loop().time()
            # wait_time = cls.last_send_time
            # cls.send_delay - now
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
        try:
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
                try:
                    return json.loads(json_text)
                except JSONDecodeError:
                    raise GenerationError(t("error.answer_not_in_json"))


            logger.error(
                t("error.wrong_gpt_answer")
            )
            return {}
        except requests.exceptions.ConnectionError:
            logger.error(
                t("error.connection_error")
            )
            return {}


class OpenAIGPTModule(SyntxModule):
    client = AsyncOpenAI()

    @classmethod
    async def _generate(
        cls,
        prompt: str,
        logger,
        photo: str | list[str] | None = None,
        model: str = "gpt-4o-mini"
    ) -> dict:
        """
        Асинхронная генерация ответа GPT с изображениями в Base64 (data URI).
        """
        temp_files: list[Path] = []

        try:
            content = [{"type": "input_text", "text": prompt}]

            if photo:
                photos = photo if isinstance(photo, (list, tuple)) else [photo]
                for p in photos:
                    tmp_path = cls._prepare_image(Path(p))
                    temp_files.append(tmp_path)

                    # кодируем в data URI
                    with open(tmp_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")

                    data_uri = f"data:image/jpeg;base64,{b64}"

                    content.append({
                        "type": "input_image",
                        "image_url": data_uri
                    })

            logger.info(t("info.gpt.generating"))
            response = await cls.client.responses.create(
                model=model,
                input=[{
                    "role": "user",
                    "content": content
                }],
            )

            logger.info(t("info.gpt.generation_end"))
            return cls._extract_json(response)

        except openai.RateLimitError as e:

            error_data = {}

            try:

                if e.response is not None:
                    error_data = e.response.json()

            except Exception:

                pass

            error_type = error_data.get("error", {}).get("type")

            if error_type == "insufficient_quota":
                raise GenerationError(

                    "Превышен бюджет проекта. Проверьте Billing.",

                    log="Превышен бюджет проекта. Проверьте Billing.",

                    fatal=True,

                )

            # обычный rate limit — можно ретраить

            raise GenerationError(

                "Слишком много запросов. Повторите позже.",

                log="Слишком много запросов. Повторите позже.",

                delay=30

            )
        finally:
            for f in temp_files:
                try:
                    f.unlink()
                except Exception:
                    pass

    @classmethod
    def _prepare_image(
        cls,
        path: Path,
    ) -> Path:
        """
        Подготовка изображения во временный файл (Windows‑safe).
        """
        if not path.exists():
            raise FileNotFoundError(path)

        fd, tmp_file_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        tmp_path = Path(tmp_file_path)
        config = cls.get_config()
        max_size = (int(config.get("max_width")), int(config.get("max_height")))
        quality = config.get("quality")

        with Image.open(path) as img:
            img = img.convert("RGB")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(tmp_path, format="JPEG", quality=quality, optimize=True, progressive=True)

        return tmp_path

    @classmethod
    async def _run(cls, name: str, logger, prompt: str, database, photo: Path | list[Path] | None = None, model: str = "gpt-4o-mini"):
        return await cls._generate(prompt=prompt, photo=photo, logger=logger, model=model)

    @staticmethod
    def _extract_json(response) -> dict:
        """
        Извлечение JSON из ответа Responses API.
        Убираем Markdown ```json ... ``` если есть.
        """
        try:
            text_output = ""

            for msg in getattr(response, "output", []):
                for item in getattr(msg, "content", []):
                    if getattr(item, "type", None) == "output_text":
                        text_output += getattr(item, "text", "")

            if not text_output.strip():
                raise GenerationError(t("error.answer_not_in_json"), delay=5)

            # Убираем возможные Markdown-блоки ```json ... ```
            text_output = re.sub(r"^```json\s*", "", text_output.strip(), flags=re.IGNORECASE)
            text_output = re.sub(r"\s*```$", "", text_output.strip())

            # Парсим JSON
            return json.loads(text_output)

        except json.JSONDecodeError:
            raise GenerationError(t("error.answer_not_in_json"), delay=5)
        except Exception as e:
            raise GenerationError(f"{t("error.wrong_gpt_answer")}: {e}")
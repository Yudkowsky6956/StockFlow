import asyncio
from pathlib import Path

from i18n import t
from pyrogram.types import Message

from src.utils.sentances import compile_prompt
from src.core.pyrogram.filters import contains
from src.modules.core_module import AgentModule
from src.modules.vars import *
from src.core.database import Database


class CoreDesignModule(AgentModule):
    category_message = DESIGN_MESSAGE
    category_response = DESIGN_RESPONSE

    flags = ""

    @classmethod
    async def download(cls, message: Message | list[Message], path: Path) -> Path | list[Path]:
        if isinstance(message, list):
            tasks = [asyncio.create_task(cls.bot().download(msg, path.with_stem(f"{path.stem}_{index}"))) for index, msg in enumerate(message, start=1)]
            return await asyncio.gather(*tasks)
        return await cls.bot().download(message, path)

    @classmethod
    async def _run(cls, name: str, logger, prompt: str, database: Database, destination: Path, upscale=True):
        config = cls.get_config()
        model_and_name = f"{config["name"]}_{name}"
        prompt = compile_prompt(model_and_name, " ".join([cls.flags, prompt]))
        message = await cls._generate(prompt=prompt, logger=logger, upscale=upscale)
        return await cls.download(message, destination / f"{model_and_name}.jpg")

class NanoModule(CoreDesignModule):
    @classmethod
    async def _generate(cls, prompt: str, logger, upscale=False) -> Message:
        async with cls.syntx_lock:
            await cls.start()
            prompt_message = await cls.bot().send(text=prompt, logger=logger)
            generating_task = asyncio.create_task(cls.bot().wait_for(
                message=prompt_message,
                flt=contains("Тариф"),
                reply=True
            ))
            logger.info(t("info.design.generating"))
            await asyncio.sleep(5)
        generating_message = await asyncio.gather(generating_task)
        original_message = await cls.bot().wait_for(
            message=prompt_message,
            flt=contains(DESIGN_QUALITY_LINK),
            logger=logger,
            request_message=generating_message,
            button_map=NANO_ORIGINAL_BUTTON_MAP
        )
        return original_message


class MidjourneyModule(CoreDesignModule):
    flags = "--ar 16:9"

    @classmethod
    async def _generate(cls, prompt: str, logger, upscale=True) -> list[Message]:
        async with cls.syntx_lock:
            await cls.start()
            prompt_message = await cls.bot().send(text=prompt, logger=logger)
            generating_task = asyncio.create_task(cls.bot().wait_for(
                message=prompt_message,
                flt=contains("Тариф"),
                reply=True
            ))
            logger.info(t("info.design.generating"))
            await asyncio.sleep(5)
        generating_message = await asyncio.gather(generating_task)
        original_message = await cls.bot().wait_for(
            message=prompt_message,
            flt=contains(YOUR_REQUEST.format(prompt[:50])),
            logger=logger,
            request_message=generating_message,
            button_map=MIDJOURNEY_DESIGN_ORIGINAL_BUTTON_MAP
        )
        if upscale:
            async with cls.syntx_lock:
                selected_tasks = [
                    asyncio.create_task(cls.bot().wait_for(
                        message=prompt_message,
                        flt=contains(DESIGN_QUALITY_LINK),
                        logger=logger,
                        button_map=MIDJOURNEY_DESIGN_SELECTED_BUTTON_MAP
                    )) for _ in range(4)
                ]

                await cls.bot().click(original_message, DESIGN_SELECT_1, logger)
                await cls.bot().click(original_message, DESIGN_SELECT_2, logger)
                await cls.bot().click(original_message, DESIGN_SELECT_3, logger)
                await cls.bot().click(original_message, DESIGN_SELECT_4, logger)

                selected_messages = await asyncio.gather(*selected_tasks)

                upscaled_tasks = [
                    asyncio.create_task(cls.bot().wait_for(
                        message=prompt_message,
                        flt=contains(DESIGN_QUALITY_LINK),
                        logger=logger,
                        photo=selected.photo,
                        button_map=MIDJOURNEY_DESIGN_UPSCALED_BUTTON_MAP
                    )) for selected in selected_messages
                ]
                for selected in selected_messages:
                    await cls.bot().click(selected, DESIGN_UPSCALE_THIN, logger)
                    await asyncio.sleep(5)
            upscaled_messages = await asyncio.gather(*upscaled_tasks)
            logger.info(t("info.design.generation_end"))
            return upscaled_messages
        else:
            logger.info(t("info.design.generation_end"))
            return [original_message]
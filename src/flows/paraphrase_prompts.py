import asyncio
import json

from loguru import logger as default_logger
from i18n import t

from src.core.syntx import GenerationError, SyntxBot
from src.core.database import Database
from src.modules import get_modules_objects
from .core_flow import Flow


class ParaphrasePrompts(Flow):
    CONFIG_PARAMETERS = ["database", "pre_template", "post_template"]


    @classmethod
    async def _task(cls, name, logger, database, pre_template, post_template, prompt):
        gpt = get_modules_objects("GPT")
        answer_dict = await gpt.run(
            name=name,
            logger=logger,
            database=database,
            prompt=pre_template.format(prompt=prompt),
            mark=False
        )
        if answer_dict is None:
            return None
        if not "prompt" in answer_dict:
            raise GenerationError(t("error.gpt.no_parameter_in_result"))
        paraphrased_prompt = post_template.format(prompt=answer_dict.get("prompt"))
        database.set_paraphrased(name, paraphrased_prompt)
        return paraphrased_prompt

    @classmethod
    async def _run(cls, tasks: list, config: dict) -> list:
        pre_template = config.get("pre_template")
        post_template = config.get("post_template")

        database_name = config.get("database")
        with Database(database_name) as db:
            gpt = get_modules_objects("GPT")
            rows = db.get_not_paraphrased()

            bot = SyntxBot()
            async with bot.client:
                for row in rows:
                    prompt = row.prompt
                    name = row.hash
                    paraphrased = row.alt_prompt
                    if not paraphrased:
                        logger = default_logger.bind(name=name, module_name=gpt.syntx_name, module_color=gpt.color)
                        tasks.append(
                            asyncio.create_task(
                                cls._task(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    prompt=prompt,
                                    pre_template=pre_template,
                                    post_template=post_template
                                )
                            )
                        )
                results = await asyncio.gather(*tasks)
                return results
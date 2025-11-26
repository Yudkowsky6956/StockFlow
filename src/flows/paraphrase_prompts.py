import asyncio

from tqdm.asyncio import tqdm_asyncio
from loguru import logger as default_logger
from i18n import t

from src.utils.sentances import wrap_by_words
from src.core.syntx import GenerationError, SyntxBot
from src.core.database import Database
from src.modules import get_modules_objects
from .core_flow import CoreFlow


class ParaphrasePrompts(CoreFlow):
    CONFIG_PARAMETERS = ["database", "pre_template", "post_template"]


    @classmethod
    async def _task(cls, name, logger, database, pre_template, post_template, prompt, gpt):
        answer_dict = await gpt.run(
            name=name,
            logger=logger,
            database=database,
            prompt=pre_template.format(prompt=prompt),
            mark=False,
        )
        if answer_dict is None:
            return None
        if not "prompt" in answer_dict:
            raise GenerationError(t("error.gpt.no_parameter_in_result"))
        paraphrased_prompt = wrap_by_words(post_template.format(prompt=answer_dict.get("prompt")))
        database.set_paraphrased(name, paraphrased_prompt)
        return paraphrased_prompt

    @classmethod
    async def _run(cls) -> list:
        default_logger.success(f"{t("info.flows.starting_flow")}: {t(f"config_flows.{cls.__name__}.choice")}")

        flow_config = cls.get_config()
        pre_template = flow_config.get("pre_template")
        post_template = flow_config.get("post_template")
        database_name = flow_config.get("database")
        unit = t(f"config_flows.{cls.__name__}.progress_unit")

        tasks = []

        gpt = get_modules_objects("GPT")
        module_name = gpt.get_name()
        module_color = gpt.get_color()

        with Database(database_name) as db:
            rows = db.get_not_paraphrased()

            async with SyntxBot().client:
                for row in rows:
                    prompt = row.prompt
                    name = row.hash
                    paraphrased = row.alt_prompt
                    logger = default_logger.bind(
                        name=name,
                        module_name=module_name,
                        module_color=module_color
                    )

                    if not paraphrased:
                        tasks.append(
                            asyncio.create_task(
                                cls._task(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    prompt=prompt,
                                    pre_template=pre_template,
                                    post_template=post_template,
                                    gpt=gpt
                                )
                            )
                        )

                return await tqdm_asyncio.gather(
                    *tasks,
                    desc=f"{module_name:<11}",
                    unit=unit
                )
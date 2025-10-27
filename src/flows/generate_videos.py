import asyncio
import yaml
from pathlib import Path

from loguru import logger as default_logger

from src.core.syntx import SyntxBot
from src.utils.interface.select import select_video_folder, select_generation_amount
from src.core.database import Database
from src.modules import get_modules_by_names
from .vars import FLOWS_YML


async def prompts_to_videos():
    filename = Path(__file__).stem
    flow_config = yaml.safe_load(FLOWS_YML.read_text(encoding="utf-8"))[filename]

    amount = flow_config["amount"]
    if not amount:
        amount = select_generation_amount()

    database = Database(flow_config["database"])
    prompts = database.get(amount)
    default_logger.info(f"Imported {len(prompts)} prompts.")

    destination = select_video_folder()

    tasks = []
    bot = SyntxBot()
    async with bot.client:
        for prompt_record in prompts:
            for module in get_modules_by_names(flow_config["modules"]):
                name = prompt_record.hash
                logger = default_logger.bind(name=name, module=module)
                tasks.append(asyncio.create_task(module.run(
                    name=name,
                    logger=logger,
                    database=database,
                    prompt=prompt_record.alt_prompt,
                    destination=destination
                )))
        results = await asyncio.gather(*tasks)
        return results


import asyncio
import traceback

from i18n import t
from loguru import logger as default_logger
from tqdm.asyncio import tqdm_asyncio

from src.core.database import Database
from src.core.global_config import get_global_config
from src.core.logger import telegram_sink
from src.core.stop_event import StopEvent
from src.core.syntx import SyntxBot
from src.interface.file_dialog import select_photos, select_video_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow


class GenerateVideosFromPhotos(CoreFlow):
    CONFIG_PARAMETERS = ["database", "prompt", "video_modules", "one_video_per_photo"]

    @classmethod
    async def _run(cls) -> list:
        try:
            default_logger.success(f"{t('info.flows.starting_flow')}: {t(f'config_flows.{cls.__name__}.choice')}")


            photos = select_photos()
            destination = select_video_folder()

            flow_config = cls.get_config()
            modules_names = flow_config.get("video_modules")
            database_name = flow_config.get("database")
            prompt = flow_config.get("prompt")
            one_video_per_photo = flow_config.get("one_video_per_photo", False)
            unit = t(f"config_flows.{cls.__name__}.progress_unit")

            modules = get_modules_objects(modules_names)
            await cls._reset_modules(modules)
            tasks = []
            results = []

            with Database(database_name) as db:
                async with SyntxBot().client:
                    if one_video_per_photo:
                        # индекс для кругового выбора видео-модуля
                        video_index = 0
                        for photo in photos:
                            module = modules[video_index % len(modules)]
                            module_name = module.get_name()
                            module_color = module.get_color()
                            module_logger = default_logger.bind(
                                name=photo.stem,
                                module_name=module_name,
                                module_color=module_color
                            )
                            task = asyncio.create_task(
                                module.run(
                                    name=photo.stem,
                                    logger=module_logger,
                                    photo=photo,
                                    prompt=prompt,
                                    destination=destination,
                                    database=db
                                )
                            )
                            tasks.append(task)
                            video_index += 1
                    else:
                        # старая логика: все модули обрабатывают все фото
                        for module in modules:
                            module_name = module.get_name()
                            module_color = module.get_color()
                            module_tasks = []

                            for photo in photos:
                                module_logger = default_logger.bind(
                                    name=photo.stem,
                                    module_name=module_name,
                                    module_color=module_color
                                )
                                module_tasks.append(
                                    asyncio.create_task(
                                        module.run(
                                            name=photo.stem,
                                            logger=module_logger,
                                            photo=photo,
                                            prompt=prompt,
                                            destination=destination,
                                            database=db
                                        )
                                    )
                                )
                            tasks.append(
                                asyncio.create_task(
                                    tqdm_asyncio.gather(
                                        *module_tasks,
                                        desc=f"{module_name:<11}",
                                        unit=unit
                                    )
                                )
                            )

                    # ждём завершения всех задач
                    async def _watch_for_stop(tasks):
                        await StopEvent.event.wait()
                        for task in tasks:
                            task.cancel()
                    stop_watcher = asyncio.create_task(_watch_for_stop(tasks))

                    try:
                        nested_results = await asyncio.gather(*tasks)
                        for result in nested_results:
                            # для one_video_per_photo результат приходит как объект, а не список
                            if one_video_per_photo:
                                results.append(result)
                            else:
                                results.extend(result)

                        if get_global_config().get("notify_on_end"):
                            telegram_sink(t("info.flows.flow_ended").format(name=t(f"config_flows.{cls.__name__}.choice")))
                        return results
                    except asyncio.CancelledError:
                        pass
                    finally:
                        stop_watcher.cancel()

        except Exception as e:
            default_logger.critical(str(e))
            traceback.print_exc()
            return []

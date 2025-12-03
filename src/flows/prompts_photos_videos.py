import asyncio
import traceback

from i18n import t
from loguru import logger as default_logger
from tqdm import tqdm

from src.core.database import Database
from src.core.syntx import GenerationError, SyntxBot
from src.interface.file_dialog import select_photo_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow
from ..core.global_config import get_global_config
from ..core.logger import telegram_sink


class GeneratePromptsPhotosVideos(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gen_amount", "upscale", "photo_modules", "video_modules", "one_video_per_photo"]

    @classmethod
    async def _run(cls) -> tuple[list, list]:
        try:
            default_logger.success(f"{t('info.flows.starting_flow')}: {t(f'config_flows.{cls.__name__}.choice')}")
            await cls._reset_modules()

            destination = select_photo_folder()
            cfg = cls.get_config()
            amount = cfg.get("gen_amount")
            database_name = cfg.get("database")
            photo_modules_names = cfg.get("photo_modules")
            video_modules_names = cfg.get("video_modules")
            unit = t(f"config_flows.{cls.__name__}.progress_unit")

            photo_modules = get_modules_objects(photo_modules_names)
            video_modules = get_modules_objects(video_modules_names)

            photo_results = []
            video_results = []

            # прогресс-бары для видео: photo_module -> video_module
            video_bars = {
                pm: {vm: tqdm(total=amount*pm.output_amount,
                              desc=f"{pm.get_name():<11} {vm.get_name():<11}",
                              unit=unit)
                     for vm in video_modules}
                for pm in photo_modules
            }

            with Database(database_name) as db:
                all_rows = db.get(amount=amount, modules=photo_modules_names)

                async with SyntxBot().client:

                    loop = asyncio.get_event_loop()
                    all_tasks = set()  # общий набор всех задач

                    # --- callback ---

                    def make_photo_done(bar, photo_module, paraphrased):
                        # индекс для кругового выбора видео модуля
                        video_index = 0

                        def callback(task: asyncio.Task):
                            nonlocal video_index
                            try:
                                photos = task.result()
                                if not isinstance(photos, list):
                                    photos = [photos]
                                if photos:
                                    photo_results.extend(photos)
                            finally:
                                bar.update()

                            missing_photos = photo_module.output_amount - len(photos)
                            if missing_photos > 0:
                                # если фото не хватило, обновляем все бары видео
                                if not cls.get_config().get("one_video_per_photo"):
                                    for vm in video_modules:
                                        vbar = video_bars[photo_module][vm]
                                        vbar.update(missing_photos)

                            # --- создаём видео задачи ---
                            for photo in photos:
                                if cls.get_config().get("one_video_per_photo"):
                                    # берем один видео-модуль по кругу
                                    vm = video_modules[video_index % len(video_modules)]
                                    vbar = video_bars[photo_module][vm]
                                    video_logger = default_logger.bind(
                                        name=photo.stem,
                                        module_name=vm.get_name(),
                                        module_color=vm.get_color(),
                                    )
                                    vtask = asyncio.get_event_loop().create_task(
                                        vm.run(
                                            name=photo.stem,
                                            prompt=paraphrased,
                                            photo=photo,
                                            logger=video_logger,
                                            database=db,
                                            mark=False,
                                            destination=destination,
                                        )
                                    )
                                    vtask.add_done_callback(lambda t, b=vbar: b.update())
                                    all_tasks.add(vtask)
                                    video_index += 1  # следующий модуль
                                else:
                                    # старая логика: все видео модули
                                    for vm in video_modules:
                                        vbar = video_bars[photo_module][vm]
                                        video_logger = default_logger.bind(
                                            name=photo.stem,
                                            module_name=vm.get_name(),
                                            module_color=vm.get_color(),
                                        )
                                        vtask = asyncio.get_event_loop().create_task(
                                            vm.run(
                                                name=photo.stem,
                                                prompt=paraphrased,
                                                photo=photo,
                                                logger=video_logger,
                                                database=db,
                                                mark=False,
                                                destination=destination,
                                            )
                                        )
                                        vtask.add_done_callback(lambda t, b=vbar: b.update())
                                        all_tasks.add(vtask)

                        return callback

                    # --- создаём фото задачи ---
                    for pm in photo_modules:
                        pm_name = pm.get_name()
                        pm_color = pm.get_color()
                        pm_rows = all_rows[pm_name]
                        pm_bar = tqdm(total=amount, desc=f"{pm_name:<23}", unit=unit)

                        for row in pm_rows:
                            paraphrased = row.alt_prompt
                            name = row.hash
                            logger = default_logger.bind(
                                name=name,
                                module_name=pm_name,
                                module_color=pm_color,
                            )
                            task = loop.create_task(
                                pm.run(
                                    name=name,
                                    logger=logger,
                                    database=db,
                                    prompt=paraphrased,
                                    destination=destination,
                                )
                            )
                            task.add_done_callback(make_photo_done(pm_bar, pm, paraphrased))
                            all_tasks.add(task)

                    # ждём завершения всех задач (фото + видео)
                    await asyncio.gather(*all_tasks)

            if get_global_config().get("notify_on_end"):
                telegram_sink(t("info.flows.flow_ended").format(name=t(f"config_flows.{cls.__name__}.choice")))
            return photo_results, video_results

        except GenerationError as e:
            return [], []

        except Exception as e:
            default_logger.critical(str(e))
            traceback.print_exc()
            return [], []

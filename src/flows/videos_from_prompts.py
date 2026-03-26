import asyncio
import traceback

from i18n import t
from loguru import logger as default_logger
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

from src.core.image_file import ImageFile
from src.interface.file_dialog import select_photos
from src.interface.async_console_dialog import ask_double
from src.core.database import Database
from src.core.global_config import get_global_config
from src.core.logger import telegram_sink
from src.core.stop_event import StopEvent
from src.core.syntx import SyntxBot
from src.interface.file_dialog import select_video_folder
from src.modules import get_modules_objects
from .core_flow import CoreFlow
from .generate_metadata import GenerateMetadata


class GenerateVideosFromPrompts(CoreFlow):
    CONFIG_PARAMETERS = ["database", "gen_amount", "video_modules", "one_video_per_prompt", "additional_metadata"]

    @classmethod
    async def _run(cls) -> list:
        try:
            default_logger.success(
                f"{t('info.flows.starting_flow')}: "
                f"{t(f'config_flows.{cls.__name__}.choice')}"
            )

            destination = select_video_folder()

            cfg = cls.get_config()
            metadata_cfg = GenerateMetadata.get_config()

            amount = cfg.get("gen_amount")
            modules_names = cfg.get("video_modules")
            database_name = cfg.get("database")
            one_video_per_prompt = cfg.get("one_video_per_prompt", True)
            additional_metadata = cfg.get("additional_metadata", True)
            unit = t(f"config_flows.{cls.__name__}.progress_unit")
            modules = get_modules_objects(modules_names)
            if not modules:
                return []
            await cls._reset_modules(modules)

            if additional_metadata:
                photos = select_photos()
                double = await ask_double()
                metadata_template = metadata_cfg.get("gpt_template")
                metadata_database = metadata_cfg.get("database")
                metadata_photos = []
                for photo_path in photos:
                    photo = ImageFile(photo_path)
                    if not (photo.title or photo.description or photo.keywords):
                        metadata_photos.append(photo)
                metadata_gpt = get_modules_objects("GPT")
                metadata_name = metadata_gpt.get_name()
                metadata_color = metadata_gpt.get_color()
                metadata_unit = t(f"config_flows.{GenerateMetadata.__name__}.progress_unit")
                await cls._reset_modules([metadata_gpt])

            results = []
            all_tasks = set()

            # индексация для циклического выбора модулей
            video_index = 0

            # helper: callback factory to avoid late-binding and to always update + refresh bar
            def make_bar_callback(bar):
                def _callback(fut):
                    try:
                        # try to read result to re-raise exception if needed (optional)
                        _ = fut.result()
                    except Exception:
                        # логируем ошибку модуля — но всё равно увеличиваем бар
                        default_logger.debug("Task finished with exception (bar will still be updated).")
                    finally:
                        try:
                            bar.update(1)
                            bar.refresh()
                        except Exception:
                            pass
                return _callback

            def _collect_result_item(res):
                # helper to normalize result: modules may return list or single item
                if isinstance(res, list):
                    results.extend(res)
                else:
                    results.append(res)

            with Database(database_name) as db:
                all_rows = db.get(amount=amount, modules=modules_names)
                for module, rows in all_rows.items():
                    default_logger.info(f"Было выбрано {module}: {len(rows)} строк.")
                async with SyntxBot().client:
                    # keep track of bar positions so they don't overlap
                    bar_position = 0
                    bars = []  # so we can close them at the end

                    # --- METADATA TASKS ---
                    if additional_metadata and metadata_photos:
                        with Database(metadata_database) as meta_db:
                            metadata_bar = tqdm(
                                total=len(metadata_photos),
                                desc=f"{metadata_name:<11}",
                                unit=metadata_unit,
                                position=bar_position,
                                leave=True
                            )
                            default_logger.debug(f"Created metadata bar at position {bar_position}")
                            bar_position += 1
                            bars.append(metadata_bar)

                            for photo in metadata_photos:
                                name = photo.path.stem
                                metadata_logger = default_logger.bind(
                                    name=name,
                                    module_name=metadata_name,
                                    module_color=metadata_color
                                )

                                task = asyncio.create_task(
                                    GenerateMetadata._task(
                                        name=name,
                                        logger=metadata_logger,
                                        database=meta_db,
                                        image_file=photo,
                                        gpt_template=metadata_template,
                                        double=double,
                                        gpt=metadata_gpt
                                    )
                                )

                                task.add_done_callback(make_bar_callback(metadata_bar))
                                all_tasks.add(task)

                    # --- VIDEO TASKS: ONE VIDEO PER PROMPT ---
                    if one_video_per_prompt:
                        # создаём по одному bar'у на исходный модуль (по module_name)
                        module_bars = {}
                        for module_name in modules_names:
                            rows = all_rows.get(module_name, [])
                            module_bar = tqdm(
                                total=len(rows),
                                desc=f"{module_name:<11}",
                                unit=unit,
                                position=bar_position,
                                leave=True
                            )
                            default_logger.debug(f"Created module bar '{module_name}' at position {bar_position} (len={len(rows)})")
                            bar_position += 1
                            bars.append(module_bar)
                            module_bars[module_name] = module_bar

                        # создаём задачи; модуль выбирается циклично
                        for module_name in modules_names:
                            for row in all_rows.get(module_name, []):
                                paraphrased = row.alt_prompt
                                name = row.hash

                                # выбираем модуль по кругу
                                module = modules[video_index % len(modules)]
                                video_index += 1

                                logger = default_logger.bind(
                                    name=name,
                                    module_name=module.get_name(),
                                    module_color=module.get_color()
                                )

                                task = asyncio.create_task(
                                    module.run(
                                        name=name,
                                        logger=logger,
                                        database=db,
                                        prompt=paraphrased,
                                        destination=destination
                                    )
                                )

                                # callback привязываем к бару исходного module_name (как у тебя логично)
                                bar_for_row = module_bars[module_name]
                                task.add_done_callback(make_bar_callback(bar_for_row))
                                all_tasks.add(task)

                        # watcher отменяет задачи при StopEvent
                        async def _watch_for_stop(tasks):
                            await StopEvent.event.wait()
                            default_logger.info("StopEvent detected: cancelling tasks...")
                            for t in list(tasks):
                                try:
                                    t.cancel()
                                except Exception:
                                    pass

                        stop_watcher = asyncio.create_task(_watch_for_stop(all_tasks))

                        try:
                            # ждем выполнения всех задач; возвращаем исключения как значения
                            done_results = await asyncio.gather(*all_tasks, return_exceptions=True)
                            for r in done_results:
                                if isinstance(r, Exception):
                                    # логируем, но продолжаем
                                    default_logger.debug(f"Task finished with exception: {r}")
                                else:
                                    # нормализуем
                                    if isinstance(r, list):
                                        results.extend(r)
                                    else:
                                        results.append(r)
                        except asyncio.CancelledError:
                            # если сборка сама была отменена
                            pass
                        finally:
                            stop_watcher.cancel()
                            # закрываем бары
                            for b in bars:
                                try:
                                    b.close()
                                except Exception:
                                    pass

                    else:
                        # --- СТАРАЯ ЛОГИКА: каждый модуль получает свои prompts ---
                        tasks_by_module = []
                        module_bars = []

                        for idx, module in enumerate(modules):
                            module_name = module.get_name()
                            module_color = module.get_color()
                            module_rows = all_rows.get(module_name, [])

                            module_bar = tqdm(
                                total=len(module_rows),
                                desc=f"{module_name:<11}",
                                unit=unit,
                                position=bar_position,
                                leave=True
                            )
                            default_logger.debug(f"Created module bar '{module_name}' at position {bar_position} (len={len(module_rows)})")
                            bar_position += 1
                            module_bars.append(module_bar)
                            bars.append(module_bar)

                            module_tasks = []
                            for row in module_rows:
                                name = row.hash
                                paraphrased = row.alt_prompt
                                logger = default_logger.bind(
                                    name=name,
                                    module_name=module_name,
                                    module_color=module_color
                                )

                                tsk = asyncio.create_task(
                                    module.run(
                                        name=name,
                                        logger=logger,
                                        database=db,
                                        prompt=paraphrased,
                                        destination=destination
                                    )
                                )
                                # каждый таск увеличивает bar этого модуля
                                tsk.add_done_callback(make_bar_callback(module_bar))
                                module_tasks.append(tsk)

                            # собираем группу задач модуля в одну задачу
                            if module_tasks:
                                tasks_by_module.append(asyncio.gather(*module_tasks, return_exceptions=True))

                        async def _watch_for_stop(tasks):
                            await StopEvent.event.wait()
                            default_logger.info("StopEvent detected: cancelling grouped module tasks...")
                            for task in tasks:
                                try:
                                    task.cancel()
                                except Exception:
                                    pass

                        stop_watcher = asyncio.create_task(_watch_for_stop(tasks_by_module))

                        try:
                            nested_results = await asyncio.gather(*tasks_by_module, return_exceptions=True)
                            for module_result in nested_results:
                                if isinstance(module_result, Exception):
                                    default_logger.debug(f"Module group finished with exception: {module_result}")
                                elif isinstance(module_result, list):
                                    # module_result is a list with results (or exceptions)
                                    for item in module_result:
                                        if isinstance(item, Exception):
                                            default_logger.debug(f"Task in module group failed: {item}")
                                        else:
                                            if isinstance(item, list):
                                                results.extend(item)
                                            else:
                                                results.append(item)
                                else:
                                    # unlikely case: single result
                                    if isinstance(module_result, list):
                                        results.extend(module_result)
                                    else:
                                        results.append(module_result)
                        except asyncio.CancelledError:
                            pass
                        finally:
                            stop_watcher.cancel()
                            for b in bars:
                                try:
                                    b.close()
                                except Exception:
                                    pass

            if get_global_config().get("notify_on_end"):
                telegram_sink(
                    t("info.flows.flow_ended")
                    .format(name=t(f"config_flows.{cls.__name__}.choice"))
                )

            return results

        except Exception as e:
            default_logger.critical(str(e))
            traceback.print_exc()
            return []
import csv
from pathlib import Path

from InquirerPy import inquirer
from i18n import t
from loguru import logger as default_logger

from src.core.database import Database
from src.interface.async_console_dialog import ask_database
from src.interface.file_dialog import select_csv
from .core_script import ScriptsDB


class ImportPromptsCSV(ScriptsDB):
    """
    Импорт промптов из CSV в базу.
    Берётся 3-й столбец CSV (index=2) как prompt.
    Пользователь выбирает режим: оригинал или парафраз.
    """

    question_locale = "info.scripts.import_prompts.question"
    original_answer_locale = "info.scripts.import_prompts.original_answer"
    paraphrased_answer_locale = "info.scripts.import_prompts.paraphrased_answer"
    prompts_selected_locale = "info.scripts.import_prompts.prompts_selected"
    success_locale = "info.scripts.import_prompts.success"
    file_not_found_locale = "error.scripts.import_prompts.file_not_found"

    BATCH_SIZE = 500  # количество вставляемых записей за раз

    @classmethod
    async def _run(cls):
        logger = default_logger.bind(module_name=cls.__name__)

        file_path: Path = select_csv()
        if not file_path or not file_path.exists():
            logger.error(t(cls.file_not_found_locale))
            return

        # выбор режима импорта
        choice = await inquirer.select(
            message=t(cls.question_locale),
            choices=[t(cls.original_answer_locale), t(cls.paraphrased_answer_locale)]
        ).execute_async()

        db_name = await ask_database()
        if not db_name:
            return

        # читаем CSV лениво, сразу формируем записи для bulk-вставки
        prompts_to_insert = []
        with file_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                value = row[2].strip()
                if not value:
                    continue
                if choice == t(cls.original_answer_locale):
                    prompts_to_insert.append({"prompt": value, "alt_prompt": ""})
                else:
                    prompts_to_insert.append({"prompt": "", "alt_prompt": value})

        if not prompts_to_insert:
            logger.warning(
                t(cls.prompts_selected_locale),
                amount=0,
                filename=file_path.name
            )
            return

        logger.info(
            t(cls.prompts_selected_locale),
            amount=len(prompts_to_insert),
            filename=file_path.name
        )

        # bulk-вставка в БД с прогресс-баром
        with Database(db_name) as db:
            db.insert_prompts_bulk(prompts_to_insert, batch_size=cls.BATCH_SIZE)

        logger.success(
            t(cls.success_locale),
            amount=len(prompts_to_insert),
            type=choice,
            database=db_name
        )

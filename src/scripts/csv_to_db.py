from pathlib import Path
import csv

from i18n import t
from loguru import logger as default_logger

from src.core.database import Database
from src.interface.async_console_dialog import ask_database
from .core_script import FilesScripts


class ImportPromptsFromCSV(FilesScripts):
    """
    Импорт промптов из CSV-файла в sqlite.

    Ожидаемый CSV:
    - 3-я колонка (index 2) содержит prompt
    - пустые prompt'ы пропускаются
    """

    file_not_found_locale = "info.scripts.import_prompts_csv.file_not_found"
    prompts_found_locale = "info.scripts.import_prompts_csv.prompts_found"
    prompts_inserted_locale = "info.scripts.import_prompts_csv.prompts_inserted"

    @classmethod
    async def _run(cls):
        logger = default_logger.bind(module_name=cls.__name__)

        # выбор базы данных
        db_name = await ask_database()
        if not db_name:
            return
        db = Database(db_name)

        # путь к CSV — предполагается, что FilesScripts его предоставляет
        csv_path = Path(cls.path) if hasattr(cls, "path") else None
        if not csv_path or not csv_path.exists():
            logger.error(t(cls.file_not_found_locale))
            return

        prompts = []
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"')
            for row in reader:
                if len(row) <= 2:
                    continue
                prompt = row[2].strip()
                if not prompt:
                    continue
                prompts.append(prompt)

        logger.info(t(cls.prompts_found_locale), amount=len(prompts))
        if not prompts:
            return

        inserted = 0
        for prompt in prompts:
            db.insert_prompt(
                prompt=prompt,
            )
            inserted += 1

        logger.info(
            t(cls.prompts_inserted_locale),
            amount=inserted,
            database=db_name,
        )

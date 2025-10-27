from loguru import logger

from pathlib import Path

from src.core.database import Database
from .select import select_images_and_videos, select_database


def import_hash():
    files = [Path(file) for file in select_images_and_videos()]

    prepare_list = []
    for file in files:
        if file.is_file():
            _split = file.stem.split("_")
            if len(_split) == 2:
                prepare_list.append(_split)

    db_name = select_database()
    if not db_name:
        print("Имя базы данных не задано. Выход.")
        return

    db = Database(db_name)

    # 4. Помечаем все найденные хеши как сделанные для модуля "SORA"
    for module, _hash in prepare_list:
        db.mark_done(value=_hash, module=module)

    logger.info(f"Помечено как сделанные {len(prepare_list)} записей в базе {db_name}.")

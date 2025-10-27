from loguru import logger
from i18n import t

from pathlib import Path

from src.core.database import Database
from src.interface.select import select_photos_and_videos, select_database


def mark_files_as_done():
    files = [Path(file) for file in select_photos_and_videos()]

    prepare_list = []
    for file in files:
        if file.is_file():
            _split = file.stem.split("_")
            if len(_split) == 2:
                prepare_list.append(_split)
    logger.info(t("info.scripts.mark_files_as_done.files_found"), amount=len(prepare_list))
    if not prepare_list:
        return

    db_name = select_database()
    if not db_name:
        return
    db = Database(db_name)

    for module, _hash in prepare_list:
        db.mark_done(value=_hash, module=module)

    logger.info(t("info.scripts.mark_files_as_done.marked_done"), amount=len(prepare_list), database=db_name)

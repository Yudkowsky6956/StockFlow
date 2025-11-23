from loguru import logger
from i18n import t

from src.core.image_file import ImageFile
from src.interface.file_dialog import select_photos


def clear_metadata():
    message = t("info.scripts.clear_metadata.message")
    photos_selected = t("info.scripts.clear_metadata.photos_selected")
    success = t("info.scripts.clear_metadata.final")

    photos = select_photos(title=message)
    logger.info(photos_selected, amount=len(photos))

    for photo in photos:
        ImageFile(photo).clear()

    logger.success(success, amount=len(photos))
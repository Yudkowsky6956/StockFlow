from i18n import t
from loguru import logger as default_logger

from src.core.image_file import ImageFile
from src.interface.file_dialog import select_photos
from .core_script import FilesScripts


class ClearMetadata(FilesScripts):
    message_locale = "info.scripts.clear_metadata.message"
    photos_selected_locale = "info.scripts.clear_metadata.photos_selected"
    success_locale = "info.scripts.clear_metadata.final"
    no_photos_locale = "info.scripts.clear_metadata.no_files"

    @classmethod
    async def _run(cls):
        logger = default_logger.bind(module_name=cls.__name__)

        try:
            photos = select_photos(title=t(cls.message_locale))
        except RuntimeError:
            logger.info(t(cls.no_photos_locale))
            return
        logger.info(t(cls.photos_selected_locale), amount=len(photos))

        for photo in photos:
            ImageFile(photo).clear()

        logger.success(t(cls.success_locale), amount=len(photos))

import os
import shutil

from i18n import t
from loguru import logger

from src.interface.file_dialog import select_files
from .core_script import FilesScripts


class OrganizeFiles(FilesScripts):
    message_locale = "info.scripts.organize_files.message"
    files_selected_locale = "info.scripts.organize_files.files_selected"
    moved_file_locale = "info.scripts.organize_files.moved_file"
    final_locale = "info.scripts.organize_files.final"
    no_files_locale = "info.scripts.organize_files.no_files"

    @classmethod
    async def _run(cls):
        try:
            files = select_files(title=t(cls.message_locale))
        except RuntimeError:
            logger.info(t(cls.no_files_locale))
            return

        logger.info(t(cls.files_selected_locale), amount=len(files))

        for file_path in files:
            filename = os.path.basename(file_path)
            prefix = filename.split('_')[0] if '_' in filename else "Others"
            base_dir = os.path.dirname(file_path)
            target_dir = os.path.join(base_dir, prefix)

            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            shutil.move(file_path, target_path)

            logger.info(t(cls.moved_file_locale), filename=filename, folder=target_dir)

        unique_folders = len(set(
            f.split('_')[0] if '_' in f else "Others" for f in map(os.path.basename, files)
        ))
        logger.success(t(cls.final_locale), amount=len(files), folders=unique_folders)
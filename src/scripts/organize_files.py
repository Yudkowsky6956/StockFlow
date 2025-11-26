import os
import shutil
from loguru import logger
from i18n import t
from src.interface.file_dialog import select_files

def organize_files():
    # Select files
    message = t("info.scripts.organize_files.message")
    files_selected = t("info.scripts.organize_files.files_selected")
    moved_file = t("info.scripts.organize_files.moved_file")
    final = t("info.scripts.organize_files.final")

    try:
        files = select_files(title=message)  # Можно переименовать select_photos в select_files, если есть
    except RuntimeError:
        logger.info(t("info.scripts.organize_files.no_files"))
        return


    logger.info(files_selected, amount=len(files))

    for file_path in files:
        filename = os.path.basename(file_path)
        # Определяем папку по префиксу до первого '_', если нет '_' — помещаем в "Others"
        prefix = filename.split('_')[0] if '_' in filename else "Others"
        base_dir = os.path.dirname(file_path)
        target_dir = os.path.join(base_dir, prefix)

        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, filename)
        shutil.move(file_path, target_path)

        logger.info(moved_file, filename=filename, folder=target_dir)

    unique_folders = len(set(f.split('_')[0] if '_' in f else "Others" for f in map(os.path.basename, files)))
    logger.success(final, amount=len(files), folders=unique_folders)

if __name__ == "__main__":
    organize_files()
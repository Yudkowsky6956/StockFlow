import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from i18n import t
from loguru import logger


def _get_root():
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.update()
    root.withdraw()
    return root

def select_folder(title: str = "info.interface.select.folder", **kwargs) -> Path:
    """Общая функция для выбора папки."""
    logger.info(f"{title}…")
    folder = filedialog.askdirectory(title=t(title), parent=_get_root(), **kwargs)
    if folder:
        logger.info(t("info.flows.folder_selected"), folder=Path(folder).resolve())
        return Path(folder)
    raise RuntimeError(t("error.interface.select.folder_not_selected"))

def select_files(title: str = "info.interface.select.files", **kwargs):
    """Общая функция для выбора файлы."""
    logger.info(f"{title}…")
    files = filedialog.askopenfilenames(title=t(title), parent=_get_root(), **kwargs)
    if files:
        logger.info(t("info.flows.files_selected_in_folder"), folder=Path(files[0]).resolve().parent)
        return [Path(file) for file in files]
    raise RuntimeError(t("error.interface.select.files_not_selected"))

def select_file(title: str = "info.interface.select.file", **kwargs):
    """Общая функция для выбора файла"""
    logger.info(f"{title}…")
    file = filedialog.askopenfilename(title=t(title), parent=_get_root(), **kwargs)
    if file:
        logger.info(t("info.flows.file_selected"), folder=Path(file).resolve().parent)
        return Path(file)
    raise RuntimeError(t("error.interface.select.file_not_selected"))

def select_txt(title: str = "info.interface.select.txt", filetype: str = "info.interface.select.txt_filetype", **kwargs):
    """Выбор .txt файла."""
    return select_file(title=t(title), filetypes=[(t(filetype), "*.txt")], **kwargs)

def select_scv(title: str = "info.interface.select.csv", filetype: str = "info.interface.select.csv_filetype", **kwargs):
    """Выбор .scv файла."""
    return select_file(title=t(title), filetypes=[(t(filetype), "*.csv")], **kwargs)

def select_photos(title: str = "info.interface.select.photos", filetype: str = "info.interface.select.photos_filetype", **kwargs):
    """Выбор изображений."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.jpg")], **kwargs)

def select_videos(title: str = "info.interface.select.videos", filetype: str = "info.interface.select.videos_filetype",  **kwargs):
    """Выбор видео."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.mp4")], **kwargs)

def select_photos_and_videos(title: str = "info.interface.select.photos_videos", filetype: str = "info.interface.select.photos_videos_filetype", **kwargs):
    """Выбор изображений/видео."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.jpg;*.mp4")], **kwargs)

def select_video_folder(title: str = "info.interface.select.video_folder"):
    """Выбор папки для сохранения видео."""
    return select_folder(title=t(title))

def select_photo_folder(title: str = "info.interface.select.photo_folder"):
    """Выбор папки для сохранения фотографий."""
    return select_folder(title=t(title))

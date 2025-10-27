from pathlib import Path

from loguru import logger
from i18n import t

import tkinter as tk
from tkinter import filedialog, simpledialog


def _get_root():
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.update()
    root.withdraw()
    return root

def select_folder(title: str = "info.interface.select.folder", **kwargs) -> Path:
    """Общая функция для выбора папки."""
    logger.info(f"{title}...")
    folder = filedialog.askdirectory(title=t(title), parent=_get_root(), **kwargs)
    if folder:
        return Path(folder)
    raise RuntimeError(t("error.interface.select.folder_not_selected"))

def select_amount(title: str = "info.interface.select.amount", prompt: str = "info.interface.select.amount", **kwargs) -> int:
    """Общая функция для выбора кол-ва."""
    return simpledialog.askinteger(title=t(title), prompt=t(prompt), parent=_get_root(), **kwargs)

def select_string(title: str = "info.interface.select.string", prompt: str = "info.interface.select.string", **kwargs) -> str:
    """Общая функция для выбора строки."""
    return simpledialog.askstring(title=t(title), prompt=t(prompt), parent=_get_root(), **kwargs)

def select_files(title: str = "info.interface.select.files", **kwargs):
    """Общая функция для выбора файлы."""
    logger.info(f"{title}...")
    files = filedialog.askopenfilenames(title=t(title), parent=_get_root(), **kwargs)
    if files:
        return [Path(file) for file in files]
    raise RuntimeError(t("error.interface.select.files_not_selected"))

def select_file(title: str = "info.interface.select.file", **kwargs):
    """Общая функция для выбора файла"""
    logger.info(f"{title}...")
    file = filedialog.askopenfilename(title=t(title), parent=_get_root(), **kwargs)
    if file:
        return Path(file)
    raise RuntimeError(t("error.interface.select.file_not_selected"))

def select_txt(title: str = "info.interface.select.txt", filetype: str = "info.interface.select.txt_filetype", **kwargs):
    """Выбор изображений."""
    return select_file(title=t(title), filetypes=[(t(filetype), "*.txt")], **kwargs)

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

def select_generation_amount(title: str = "info.interface.select.generations_amount"):
    """Выбор кол-ва генераций."""
    return select_amount(title=t(title), prompt=t(title), initialvalue=1000, minvalue=0)

def select_database(title: str = "info.interface.select.database"):
    """Выбор базы данных."""
    return select_string(title=t(title), prompt=t(title))

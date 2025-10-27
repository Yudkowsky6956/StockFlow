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

def select_folder(title: str = "info.utils.select.folder", **kwargs):
    """Общая функция для выбора папки."""
    logger.info(f"{title}...")
    folder = filedialog.askdirectory(title=t(title), parent=_get_root(), **kwargs)
    if folder:
        return Path(folder)
    raise RuntimeError(t("error.utils.select.folder_not_selected"))

def select_amount(title: str = "info.utils.select.amount", prompt: str = "info.utils.select.amount", **kwargs) -> int:
    """Общая функция для выбора кол-ва."""
    return simpledialog.askinteger(title=t(title), prompt=t(prompt), parent=_get_root(), **kwargs)

def select_string(title: str = "info.utils.select.string", prompt: str = "info.utils.select.string", **kwargs) -> str:
    """Общая функция для выбора строки."""
    return simpledialog.askstring(title=t(title), prompt=t(prompt), parent=_get_root(), **kwargs)

def select_files(title: str = "info.utils.select.files", **kwargs):
    """Общая функция для выбора файлы."""
    return filedialog.askopenfilenames(title=t(title), parent=_get_root(), **kwargs)

def select_photos(title: str = "info.utils.select.photos", filetype: str = "info.utils.select.photos_small", **kwargs):
    """Выбор изображений."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.jpg")], **kwargs)

def select_videos(title: str = "info.utils.select.videos", filetype: str = "info.utils.select.videos_small",  **kwargs):
    """Выбор видео."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.mp4")], **kwargs)

def select_photos_and_videos(title: str = "info.utils.select.photos_videos", filetype: str = "info.utils.select.photos_videos_small", **kwargs):
    """Выбор изображений/видео."""
    return select_files(title=t(title), filetypes=[(t(filetype), "*.jpg;*.mp4")], **kwargs)

def select_video_folder(title: str = "info.utils.select.video_folder"):
    """Выбор папки для сохранения видео."""
    return select_folder(title=t(title))

def select_photo_folder(title: str = "info.utils.select.photo_folder"):
    """Выбор папки для сохранения фотографий."""
    return select_folder(title=t(title))

def select_generation_amount(title: str = "info.utils.select.generations_amount"):
    """Выбор кол-ва генераций."""
    return select_amount(title=t(title), prompt=t(title), initialvalue=1000, minvalue=0)

def select_database(title: str = "info.utils.select.database"):
    """Выбор базы данных."""
    return select_string(title=t(title), prompt=t(title))

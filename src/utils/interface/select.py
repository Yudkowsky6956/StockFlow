from pathlib import Path

import tkinter as tk
from tkinter import filedialog, simpledialog

def get_root():
    root = tk.Tk()
    root.withdraw()
    return root

def select_folder(title="Выберите папку", **kwargs):
    """Общая функция для выбора папки"""
    folder = filedialog.askdirectory(title=title, parent=get_root(), **kwargs)
    if folder:
        return Path(folder)
    return RuntimeError("Папка не выбрана")

def select_amount(title: str = "Выберите кол-во", prompt: str = "Выберите кол-во", **kwargs) -> int:
    """Общая функция для выбора кол-ва"""
    return simpledialog.askinteger(title=title, prompt=prompt, parent=get_root(), **kwargs)

def select_string(title: str = "Впишите строку", prompt: str = "Впишите строку", **kwargs) -> str:
    return simpledialog.askstring(title=title, prompt=prompt, parent=get_root(), **kwargs)

def select_files(title="Выберите файлы", **kwargs):
    """Общая функция для выбора файлы"""
    return filedialog.askopenfilenames(title=title, parent=get_root(), **kwargs)

def select_images(title="Выберите изображения", **kwargs):
    """Общая функция для выбора изображений"""
    return select_files(title=title, filetypes=[("Изображения", "*.jpg")], **kwargs)

def select_images_and_videos(title="Выберите изображения/видео", **kwargs):
    return select_files(title=title, filetypes=[("Изображения", "*.jpg;*.mp4")], **kwargs)

def select_video_folder():
    """Выбор папки для сохранения видео"""
    return select_folder(title="Выберите папку для сохранения видео")

def select_photo_folder():
    """Выбор папки для сохранения фотографий"""
    return select_folder(title="Выберите папку для сохранения фото")

def select_generation_amount():
    """Выбор кол-ва генераций"""
    return select_amount(title="Кол-во генераций", prompt="Выберите кол-во генераций", initialvalue=1000, minvalue=0)

def select_database():
    """Выбор базы данных"""
    return select_string(title="Выбор базы данных", prompt="Впишите название базы данных (без .db)")

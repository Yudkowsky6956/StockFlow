import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from .select import select_database
from src.core.database import Database


def import_prompts():
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    # 1️⃣ Выбор .txt файла
    file_path = filedialog.askopenfilename(
        title="Выберите .txt файл с промптами",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        messagebox.showinfo("Отмена", "Файл не выбран")
        return

    # 2️⃣ Выбор типа импорта
    choice = messagebox.askquestion(
        "Выберите тип импорта",
        "Импортировать как original prompts (prompt) или paraphrased prompts (alt_prompt)?\n\nДа = original, Нет = paraphrased"
    )

    column_type = "prompt" if choice == "yes" else "alt_prompt"

    # 3️⃣ Ввод названия базы данных
    db_name = select_database()
    if not db_name:
        messagebox.showinfo("Отмена", "Название базы не введено")
        return

    # 4️⃣ Создаём/открываем базу и импортируем
    db = Database(db_name)

    with open(file_path, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]

    if column_type == "prompt":
        db.import_prompts(prompts)
    else:
        db.import_alt_prompts(prompts)

    messagebox.showinfo("Готово", f"Импортировано {len(prompts)} строк в {column_type} колонки базы {db_name}.db")
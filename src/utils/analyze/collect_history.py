import json
import re
from datetime import datetime

from .vars import *

# VARS
BOT_NAME = "Syntx AI"
REPLACE_NUMBERS = "<NUMBER>"
ERROR_MARKS = ["❌", "⚠️", "⚠"]
ANTI_ERROR_MARKS = [
    "🚨", "Вот прямая ссылка на качественную версию.",
    "[СИСТЕМНОЕ СООБЩЕНИЕ]", "[⚠️ BETA]"
]
MODEL_LIST = [
    "MidJourney", "GPT-4o", "RunWay", "Sora", "Veo", "🌄 MidJourney",
    "🏞 MidJourney", "Gemini 2.5 Pro NEW", "GPT 3", "GPT 5", "SUNO",
    "GPT-o4 Mini", "DeepSeek V3", "GPT 4", "GPT 3.5", "🎞️ RunWay: Gen-4"
]

# PATTERNS
MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n{2,}")
BLOCK_REASON_PATTERN = re.compile(r"(Недопустимый запрос:\s*).*", re.IGNORECASE)
TARIFF_PATTERN = re.compile(r"(👑 ULTRA ELITE|💣 ELITE|💎 VIP)")
INVALID_PARAM_PATTERN = re.compile(r"(invalid_parameter:\s*).*", re.IGNORECASE)
BRACKETS_PATTERN = re.compile(r"\(.*?\)")
MODEL_PATTERN = re.compile("|".join(re.escape(m) for m in MODEL_LIST), re.IGNORECASE)
TIME_PATTERN = re.compile(rf"{REPLACE_NUMBERS}:{REPLACE_NUMBERS}(?::{REPLACE_NUMBERS})?")
DELETE_AFTER_PATTERNS = [
    r"Максимальное количество одновременных генераций для тарифа <TARIFF_LEVEL>:.*",
    r"<INVALID_PARAMETER>.*",
    r"Пожалуйста, соблюдайте правила чат-бота\..*",
    r"❓.*"
]
SUPPORT_PATTERN = re.compile(r"@.*")



def ensure_folders_exist():
    """
    Создаёт необходимые папки для истории и вывода, если их нет.
    """
    HISTORY_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def get_text_from_message(message: dict) -> str:
    """
    Получаем текст из сообщения.
    Только поле 'text', text_entities игнорируются.
    """
    text = message.get("text", "")
    if isinstance(text, list):
        text_str = ""
        for t in text:
            if isinstance(t, str):
                text_str += t
            elif isinstance(t, dict) and "text" in t:
                text_str += t["text"]
        return text_str
    return str(text)


def is_marked_error(message_text: str) -> bool:
    """
    Проверяет, является ли сообщение ошибкой от бота.
    Учитывает ERROR_MARKS и ANTI_ERROR_MARKS.
    """
    if any(anti_mark in message_text for anti_mark in ANTI_ERROR_MARKS):
        return False
    return any(mark in message_text for mark in ERROR_MARKS)


def normalize_numbers(text: str) -> str:
    """
    Заменяет все числа в тексте на <NUMBER>.
    """
    return re.sub(r'\d+', REPLACE_NUMBERS, text)

def normalize_delete_after(text: str) -> str:
    """Удаляет всё после определённых ключевых фраз."""
    for pat in DELETE_AFTER_PATTERNS:
        text = re.sub(pat, "", text)
    return text

def normalize_tariff_level(text: str) -> str:
    """Заменяет тарифы TARIFF_PATTERN на <TARIFF_LEVEL>"""
    return TARIFF_PATTERN.sub("<TARIFF_LEVEL>", text)

def normalize_support(text: str) -> str:
    """Заменяет всё после '@' включая '@' на <SUPPORT>"""
    return SUPPORT_PATTERN.sub("<SUPPORT>", text)

def normalize_invalid_parameter(text: str) -> str:
    """Заменяет INVALID_PARAM_PATTERN паттерн на <INVALID_PARAMETER>"""
    return INVALID_PARAM_PATTERN.sub(r"\1<INVALID_PARAMETER>", text)

def normalize_time(text: str) -> str:
    """Заменяет HH:MM:SS или HH:MM на <TIME>"""
    return TIME_PATTERN.sub("<TIME>", text)

def normalize_brackets(text: str) -> str:
    """Заменяет всё, что внутри скобок, на <BRACKETS>"""
    return BRACKETS_PATTERN.sub("<BRACKETS>", text)

def normalize_models(text: str) -> str:
    """Заменяет все упоминания моделей/сервисов на <MODEL>"""
    return MODEL_PATTERN.sub("<MODEL>", text)

def normalize_newlines(text: str) -> str:
    """
    Заменяет несколько подряд идущих переносов строк на один.
    Например, '\n\n\n' -> '\n'
    """
    return MULTIPLE_NEWLINES_PATTERN.sub("\n", text)


# noinspection GrazieInspection
def normalize_block_reason(text: str) -> str:
    # noinspection GrazieInspection
    """
        Заменяет всё после "Недопустимый запрос: " на <BLOCK_REASON>
        """
    return BLOCK_REASON_PATTERN.sub(r"\1<BLOCK_REASON>", text)

def normalize_delete_and_support(text: str) -> str:
    """
    Объединяет уже существующие нормализации удаления/замены:
    - всё после ключевых фраз (delete_after)
    - всё после '@' на <SUPPORT>
    """
    text = normalize_support(text)
    text = normalize_delete_after(text)
    return text


def normalize_message_text(text: str) -> str:
    """Применяет все нормализации к тексту сообщения"""
    text = normalize_tariff_level(text)
    text = normalize_invalid_parameter(text)
    text = normalize_brackets(text)
    text = normalize_models(text)
    text = normalize_numbers(text)
    text = normalize_time(text)
    text = normalize_delete_and_support(text)
    text = normalize_block_reason(text)
    text = normalize_newlines(text)
    return text.strip()


# noinspection SpellCheckingInspection
def extract_date_from_message(message: dict) -> str:
    """
    Извлекает дату из сообщения в формате 'DD.MM.YYYY'.
    Предполагается, что поле 'date' в формате ISO 'YYYY-MM-DD' или 'YYYY-MM-DDTHH:MM:SS'.
    """
    date_str = message.get("date", "")
    if not date_str:
        return "unknown"
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        return "unknown"


def process_history_file(json_file: Path, counter: dict, daily_counter: dict):
    """
    Обрабатывает один JSON-файл истории и обновляет счетчики ошибок.
    Нормализует текст сообщений и распределяет их по дням.
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {json_file}, пропускаем.")
        return

    for msg in data.get("messages", []):
        if msg.get("from") != BOT_NAME:
            continue

        text_str = get_text_from_message(msg)
        if not is_marked_error(text_str):
            continue

        normalized_text = normalize_message_text(text_str)

        # общий счетчик
        counter[normalized_text] = counter.get(normalized_text, 0) + 1

        # счетчик по дням
        day = extract_date_from_message(msg)
        if day not in daily_counter:
            daily_counter[day] = {}
        daily_counter[day][normalized_text] = daily_counter[day].get(normalized_text, 0) + 1


def save_counter_to_file(counter: dict, output_file: Path):
    """
    Сохраняет подсчитанные ошибки в JSON-файл, сортируя их по убыванию количества.
    """
    result = [{"text": k, "amount": v} for k, v in counter.items()]
    result.sort(key=lambda x: x["amount"], reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def save_daily_counter_to_file(daily_counter: dict, output_file: Path):
    """
    Сохраняет ошибки по дням в JSON-файл в формате:
    {
        "01.01.2025": [
            {"text": "Ошибка X", "amount": 10},
            ...
        ],
        ...
    }
    """
    output_data = {}
    for day, errors in daily_counter.items():
        output_data[day] = [{"text": k, "amount": v} for k, v in errors.items()]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)


def collect_history():
    """
    Собирает все ошибки бота из истории, подсчитывает их общее количество
    и распределение по дням, затем сохраняет в два JSON-файла.
    """
    ensure_folders_exist()
    counter = {}
    daily_counter = {}

    history_files = HISTORY_FOLDER.glob("*.json")
    for json_file in history_files:
        process_history_file(json_file, counter, daily_counter)

    save_counter_to_file(counter, OUTPUT_FILE)
    save_daily_counter_to_file(daily_counter, OUTPUT_BY_DAY_FILE)

    print(
        f"""
        Готово!
        Список сообщений сохранён в {OUTPUT_FILE}.
        Ошибки по дням сохранены в {OUTPUT_BY_DAY_FILE}.
        """
    )

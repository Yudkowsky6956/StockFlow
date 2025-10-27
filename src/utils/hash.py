import hashlib


def get_short_hash(value: str) -> str:
    """
    Создаёт короткий хэш длиной 8 символов, который используется для именования файлов программы.

    :param value: Строка, на основании которой создаётся хэш.
    :return: Короткий хэш, длиной в 8 символов (первые 8 символов MD5).
    :note: MD5 не подходит для криптографической защиты, используется только для идентификации.
    """
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:8]

def get_color_hash(value: str) -> str:
    """
    Создаёт HEX-цвет на основании хэша строки.

    :param value: Строка, на основании которой создаётся цвет.
    :return: HEX-цвет в формате "#RRGGBB", например "#F37A48".
    """
    return f"#{hashlib.md5(value.encode("utf-8")).hexdigest()[:6].upper()}"

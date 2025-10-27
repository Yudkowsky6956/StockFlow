def safe_int(value) -> int | None:
    """
    Безопасная версия функции int.

    :param value: Значение, которое нужно int(value).
    :return: Возвращает значение после int(value). Если была ошибка, то возвращает None.
    """
    try:
        return int(value)
    except (ValueError, TypeError, OverflowError):
        return None

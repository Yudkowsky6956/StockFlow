import textwrap


def wrap_by_words(text: str, width: int = 200, placeholder: str = "") -> str | None:
    """
    Обрезает текст по словам до указанной ширины, добавляя в конце плейсхолдер, если обрезается.

    :param text: Текст, который нужно обрезать.
    :param width: Максимальная длина возвращаемой строки.
    :param placeholder: Строка, которая будет добавлена в конце строки, если текст обрезается
    :return: Обрезанный текст. Если not text, то возвращается None.
    """

    if not text:
        return None
    return textwrap.shorten(text, width, placeholder=placeholder)


def swap_word_with_previous(text: str, target_word: str = "lifestyle") -> str | None:
    """
    Меняет местами данное слово с предыдущим в тексте.

    :param text: Текст, в котором будет выполниться замена.
    :param target_word: Слово, которое нужно переместить на позицию раньше.
    :return: Текст после замены. Если not text, то возвращает None.
    """

    if not text:
        return None

    words = text.split()
    for i in range(1, len(words)):
        if words[i] == target_word:
            words[i-1], words[i] = words[i], words[i-1]
            break
    return " ".join(words)


def compile_prompt(name: str, prompt: str = None) -> str:
    if prompt:
        prompt = f"{name} {prompt}"
    else:
        prompt = f"{name}"
    return prompt.strip()
from typing import Optional

import textwrap


def wrap_by_words(text: str, width: int = 200, placeholder: str = "") -> Optional[str]:
    if text is None:
        return None
    return textwrap.shorten(text, width, placeholder=placeholder)


def swap_with_previous(text: str, target_word: str = "lifestyle") -> Optional[str]:
    if text is None:
        return None
    words = text.split()
    for i in range(1, len(words)):
        if words[i] == target_word:
            words[i-1], words[i] = words[i], words[i-1]
            break
    return wrap_by_words(" ".join(words))
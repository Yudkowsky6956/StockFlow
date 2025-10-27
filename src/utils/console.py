import sys


UP_CHAR = "\x1b[1A"
CLEAR_CHAR = "\x1b[2K"


def clear_last_lines(amount=1) -> None:
    """
    Стирает последние "n" строк в терминале.

    :param amount: Кол-во строк, которые нужно стереть.
    """
    for _ in range(amount):
        sys.stdout.write(UP_CHAR)
        sys.stdout.write(CLEAR_CHAR)
    sys.stdout.flush()
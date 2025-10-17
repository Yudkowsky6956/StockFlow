from typing import Optional


def safe_int(value) -> Optional[int]:
    try:
        return int(value)
    except (ValueError, TypeError, OverflowError):
        return None

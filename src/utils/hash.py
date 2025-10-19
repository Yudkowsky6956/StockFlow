import hashlib


def short_hash(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:8]

def color_hash(value: str) -> str:
    return f"#{hashlib.md5(value.encode("utf-8")).hexdigest()[:6].upper()}"

from typing import Optional

from src.core.secrets import get_env, set_env
from src.utils.types import safe_int
from .vars import ENV_API_HASH, ENV_API_ID


def get_api_id() -> Optional[int]:
    return safe_int(get_env(ENV_API_ID))


def get_api_hash() -> Optional[str]:
    return str(get_env(ENV_API_HASH))


def set_api_id(value):
    set_env(ENV_API_ID, safe_int(value))


def set_api_hash(value):
    set_env(ENV_API_HASH, str(value))

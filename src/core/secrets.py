import os
from typing import Optional

from dotenv import load_dotenv, set_key

from .vars import SECRETS_ENV


def get_env(key: str) -> Optional[str]:
    SECRETS_ENV.touch()
    load_dotenv()
    return str(os.getenv(str(key)))


def set_env(key: str, value):
    SECRETS_ENV.touch()
    set_key(SECRETS_ENV, str(key), str(value))
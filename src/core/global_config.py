import yaml
from src.core.vars import CONFIG_FOLDER

DEBUG = False
LANG = "en"
GLOBAL_CONFIG_PATH = CONFIG_FOLDER / "global.yml"


def get_global_config() -> dict:
    return yaml.safe_load(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8")).get("GlobalSettings")
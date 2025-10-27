from .modules import Veo, Runway, Sora

MODULES_DICT = {
    "VEO": Veo,
    "RUNWAY": Runway,
    "SORA": Sora
}


def get_modules_by_names(names):
    return [MODULES_DICT.get(name) for name in names]
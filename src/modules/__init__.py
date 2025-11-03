from .modules import Veo, Runway, Sora, GPT

ALL_MODULES = {
    "GPT": GPT,
    "VEO": Veo,
    "RUNWAY": Runway,
    "SORA": Sora
}

VIDEO_MODULES = {
    "VEO": Veo,
    "RUNWAY": Runway,
    "SORA": Sora
}


def get_modules_objects(names):
    if isinstance(names, list):
        return [ALL_MODULES.get(name) for name in names]
    else:
        return ALL_MODULES.get(names)
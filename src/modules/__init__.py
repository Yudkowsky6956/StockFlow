from src.utils.lazy_import import lazy_import

Veo = lazy_import("src.modules.modules", "Veo")
Runway = lazy_import("src.modules.modules", "Runway")
Sora = lazy_import("src.modules.modules", "Sora")
MiniMax = lazy_import("src.modules.modules", "MiniMax")
Luma = lazy_import("src.modules.modules", "Luma")
GPT = lazy_import("src.modules.modules", "GPT")
Midjourney = lazy_import("src.modules.modules", "Midjourney")
Nano = lazy_import("src.modules.modules", "Nano")


ALL_MODULES = {
    "GPT": GPT,
    "VEO": Veo,
    "RUNWAY": Runway,
    "SORA": Sora,
    "MINIMAX": MiniMax,
    "LUMA": Luma,
    "MIDJOURNEY": Midjourney,
    "NANO": Nano,
}

VIDEO_MODULES = {
    "VEO": Veo,
    "RUNWAY": Runway,
    "SORA": Sora,
    "MINIMAX": MiniMax,
    "LUMA": Luma,
}

PHOTO_MODULES = {
    "MIDJOURNEY": Midjourney,
    "NANO": Nano,
}

MODULES_LIST = list(ALL_MODULES.values())

def get_modules_objects(names):
    if isinstance(names, list):
        return [ALL_MODULES.get(name) for name in names]
    else:
        return ALL_MODULES.get(names)
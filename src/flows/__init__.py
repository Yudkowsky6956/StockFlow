from .core_flow import CoreFlow
from .generate_metadata import GenerateMetadata
from .paraphrase_prompts import ParaphrasePrompts
from .photos_from_prompts import GeneratePhotosFromPrompts
from .prompts_photos_videos import GeneratePromptsPhotosVideos
from .videos_from_photos import GenerateVideosFromPhotos
from .videos_from_prompts import GenerateVideosFromPrompts

FLOWS_LIST = [
    GenerateVideosFromPrompts,
    GenerateVideosFromPhotos,
    GeneratePhotosFromPrompts,
    ParaphrasePrompts,
    GenerateMetadata,
    GeneratePromptsPhotosVideos,
]
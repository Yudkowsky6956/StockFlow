from .videos_from_prompts import GenerateVideosFromPrompts
from .videos_from_photos import GenerateVideosFromPhotos
from .photos_from_prompts import GeneratePhotosFromPrompts
from .paraphrase_prompts import ParaphrasePrompts
from .generate_metadata import GenerateMetadata
from .prompts_photos_videos import GeneratePromptsPhotosVideos
from .core_flow import CoreFlow

FLOWS_LIST = [
    GenerateVideosFromPrompts,
    GenerateVideosFromPhotos,
    GeneratePhotosFromPrompts,
    ParaphrasePrompts,
    GenerateMetadata,
    GeneratePromptsPhotosVideos,
]
from pathlib import Path

from .metadata_manager import ImageMetadataManager


class ImageFile:
    def __init__(self, path: str | Path):
        self.path: Path = Path(path)

    @property
    def title(self) -> str:
        return ImageMetadataManager.get_title(self.path)

    @property
    def description(self) -> str:
        return ImageMetadataManager.get_description(self.path)

    @property
    def keywords(self) -> list:
        return ImageMetadataManager.get_keywords(self.path)

    @title.setter
    def title(self, value: str):
        ImageMetadataManager.set_title(self.path, value)

    @description.setter
    def description(self, value: str):
        ImageMetadataManager.set_description(self.path, value)

    @keywords.setter
    def keywords(self, value: list):
        ImageMetadataManager.set_keywords(self.path, value)

    def clear(self):
        ImageMetadataManager.clear_metadata(self.path)

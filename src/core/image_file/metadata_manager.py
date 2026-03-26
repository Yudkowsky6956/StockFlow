from pathlib import Path
from typing import Optional
import pyexiv2
import logging

from .vars import *

# Инициализируем логгер, если он не настроен в основном проекте
logger = logging.getLogger("src.core.image_file")

class ImageMetadataManager:
    @classmethod
    def get_title(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        title = cls._get_attribute(exif_title_tag, path, metadata) or ""
        return title.replace("\x00", "")

    @classmethod
    def get_description(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        description = cls._get_attribute(exif_description_tag, path, metadata) or ""
        return description.replace("\x00", "")

    @classmethod
    def get_keywords(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        keywords = cls._get_attribute(exif_keywords_tag, path, metadata) or ""
        keywords = keywords.replace("\x00", "")
        if not keywords:
            return []
        else:
            return keywords.split("; ")

    @staticmethod
    def set_title(path: Path, title: str):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_exif({exif_title_tag: title + '\x00'})
            image.modify_xmp({xmp_title_tag: title})
            image.modify_xmp({xmp_title_tag: {xmp_legacy_tag: title}})

    @staticmethod
    def set_description(path: Path, description: str):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_exif({exif_description_tag: description + '\x00'})
            image.modify_xmp({xmp_description_tag: description})

    @staticmethod
    def set_keywords(path: Path, keywords: list):
        if keywords == [""]:
            keywords = []
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_exif({exif_keywords_tag: '; '.join(keywords) + '\x00'})
            image.modify_xmp({xmp_keywords_tag: keywords})

    @staticmethod
    def clear_metadata(path: Path):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            # Используем встроенные методы очистки для безопасности
            image.clear_exif()
            image.clear_iptc()
            image.clear_xmp()

    @classmethod
    def path_to_metadata(cls, path: Path=None, metadata: tuple=None):
        if (not metadata) and (not path):
            raise ValueError("You should give path or/and metadata!")
        if not metadata and path:
            metadata = cls._get_metadata(path)
        return metadata

    @classmethod
    def _get_attribute(cls, iptc_tag: str, path: Path=None, metadata: tuple=None):
        metadata = cls.path_to_metadata(path, metadata)
        for data in metadata:
            if attribute := data.get(iptc_tag):
                return attribute

    @staticmethod
    def _get_metadata(path: Path) -> tuple[dict, ...]:
        """Безопасное получение метаданных с обработкой ошибок кодировки."""
        with pyexiv2.Image(str(path)) as image:
            try:
                # Пытаемся прочитать в стандартной кодировке
                return (image.read_exif(),)
            except UnicodeDecodeError:
                try:
                    # Если UTF-8 упал, пробуем 'latin-1' (прочитает любые байты)
                    logger.warning(f"Encoding error in {path.name}. Falling back to latin-1.")
                    return (image.read_exif(encoding='latin-1'),)
                except Exception as e:
                    logger.error(f"Failed to read metadata for {path.name}: {e}")
                    return ({},)


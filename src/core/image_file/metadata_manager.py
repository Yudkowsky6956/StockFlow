import pyexiv2

from typing import Optional
from pathlib import Path

from .vars import *


class ImageMetadataManager:
    @classmethod
    def get_title(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        return cls._get_attribute(iptc_title_tag, path, metadata) or ""

    @classmethod
    def get_description(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        return cls._get_attribute(iptc_description_tag, path, metadata) or ""

    @classmethod
    def get_keywords(cls, path: Optional[Path]=None, metadata: Optional[tuple]=None):
        return cls._get_attribute(iptc_keywords_tag, path, metadata) or []

    @staticmethod
    def set_title(path: Path, title: str):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_iptc({iptc_title_tag: title, iptc_object_tag: title})
            image.modify_exif({exif_title_tag: title + '\x00'})
            image.modify_xmp({xmp_title_tag: title})
            image.modify_xmp({xmp_title_tag: {xmp_legacy_tag: title}})

    @staticmethod
    def set_description(path: Path, description: str):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_iptc({iptc_description_tag: description})
            image.modify_exif({exif_description_tag: description + '\x00'})
            image.modify_xmp({xmp_description_tag: description})

    @staticmethod
    def set_keywords(path: Path, keywords: list):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()
            image.modify_iptc({iptc_keywords_tag: keywords})
            image.modify_exif({exif_keywords_tag: '; '.join(keywords) + '\x00'})
            image.modify_xmp({xmp_keywords_tag: keywords})

    @staticmethod
    def clear_metadata(path: Path):
        with pyexiv2.Image(str(path)) as image:
            image.clear_thumbnail()

            # Очистка IPTC
            image.modify_iptc({
                iptc_title_tag: '',
                iptc_object_tag: '',
                iptc_description_tag: '',
                iptc_keywords_tag: []
            })

            # Очистка EXIF
            image.modify_exif({
                exif_title_tag: '',
                exif_description_tag: '',
                exif_keywords_tag: ''
            })

            # Очистка XMP
            image.modify_xmp({
                xmp_title_tag: '',
                xmp_legacy_tag: '',
                xmp_description_tag: '',
                xmp_keywords_tag: []
            })

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
        with pyexiv2.Image(str(path)) as image:
            return (
                image.read_iptc(),
                pyexiv2.convert_xmp_to_iptc(pyexiv2.convert_exif_to_xmp(image.read_exif())),
                pyexiv2.convert_xmp_to_iptc(image.read_xmp())
            )
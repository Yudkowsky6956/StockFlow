import random
from typing import List, Optional

from src.utils.keywords import convert_to_double, convert_to_single, delete_intersections, unique_list


class Keywords:
    def __init__(self, keywords: List[str], primary: Optional[List[str]] = None):
        self._primary = primary or []
        self._keywords = keywords

    def run(self, double: bool) -> list:
        obj = self.single().unique().shuffle()
        if double:
            obj.double()
        return obj.get()

    def shuffle(self):
        random.shuffle(self._primary)
        random.shuffle(self._keywords)
        return self

    def unique(self):
        keywords = unique_list(self._keywords)
        self._primary = unique_list(self._primary)
        self._keywords = delete_intersections(keywords, self._primary)
        return self

    def single(self):
        self._keywords = convert_to_single(self._keywords)
        self._primary = convert_to_single(self._primary)
        return self

    def double(self):
        _keywords = convert_to_double(self._primary + self._keywords)
        _keywords = delete_intersections(_keywords, self._primary)
        self._keywords = _keywords
        return self

    def get(self, limit=50) -> List[str]:
        return (self._primary + self._keywords)[:limit]
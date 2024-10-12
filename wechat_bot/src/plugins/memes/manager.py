from enum import IntEnum
from pathlib import Path
from typing import Optional

from meme_generator.manager import get_memes
from meme_generator.meme import Meme
from pydantic import BaseModel
from rapidfuzz import process


base_path = Path(__file__).parent
config_path = str(base_path / "meme_manager.yml")


class MemeMode(IntEnum):
    BLACK = 0
    WHITE = 1


class MemeConfig(BaseModel):
    mode: MemeMode = MemeMode.BLACK
    white_list: list[str] = []
    black_list: list[str] = []

    class Config:
        use_enum_values = True


class MemeManager:
    def __init__(self, path: Path = config_path):
        self.__path = path
        self.__meme_config: dict[str, MemeConfig] = {}
        self.__meme_dict = {
            meme.key: meme
            for meme in sorted(get_memes(), key=lambda meme: meme.key)
        }
        self.__meme_names: dict[str, list[Meme]] = {}
        self.__meme_tags: dict[str, list[Meme]] = {}
        self.__load()
        self.__refresh_names()
        self.__refresh_tags()

    def get_meme(self, meme_key: str) -> Optional[Meme]:
        return self.__meme_dict.get(meme_key, None)

    def get_memes(self) -> list[Meme]:
        return list(self.__meme_dict.values())

    def find(self, meme_name: str) -> list[Meme]:
        meme_name = meme_name.lower()
        if meme_name in self.__meme_names:
            return self.__meme_names[meme_name]
        return []

    def search(
        self,
        meme_name: str,
        include_tags: bool = False,
        limit: Optional[int] = None,
        score_cutoff: float = 80.0,
    ) -> list[Meme]:
        meme_name = meme_name.lower()
        meme_names = process.extract(
            meme_name, self.__meme_names.keys(), limit=limit, score_cutoff=score_cutoff
        )
        result: dict[str, Meme] = {}
        for name, _, _ in meme_names:
            for meme in self.__meme_names[name]:
                result[meme.key] = meme
        if include_tags:
            meme_tags = process.extract(
                meme_name,
                self.__meme_tags.keys(),
                limit=limit,
                score_cutoff=score_cutoff,
            )
            for tag, _, _ in meme_tags:
                for meme in self.__meme_tags[tag]:
                    result[meme.key] = meme
        return list(result.values())

    def __load(self):
        self.__meme_config = {
            meme_key: MemeConfig() for meme_key in self.__meme_dict.keys()
        }

    def __refresh_names(self):
        self.__meme_names = {}
        for meme in self.__meme_dict.values():
            names = set()
            names.add(meme.key.lower())
            for keyword in meme.keywords:
                names.add(keyword.lower())
            for shortcut in meme.shortcuts:
                names.add((shortcut.humanized or shortcut.key).lower())
            for name in names:
                if name not in self.__meme_names:
                    self.__meme_names[name] = []
                self.__meme_names[name].append(meme)

    def __refresh_tags(self):
        self.__meme_tags = {}
        for meme in self.__meme_dict.values():
            for tag in meme.tags:
                tag = tag.lower()
                if tag not in self.__meme_tags:
                    self.__meme_tags[tag] = []
                self.__meme_tags[tag].append(meme)


meme_manager = MemeManager()

from abc import ABC, abstractmethod
from collections.abc import Iterable

from typing import Self, Tuple
from enum import StrEnum


class StringHelper:
    @staticmethod
    def indent(
        level: int, increment: int = 0, indent_base: str = "    "
    ) -> Tuple[int, str]:
        level += increment
        return level, indent_base * level


class ThemeNames(StrEnum):
    # For actual list see: https://mermaid.js.org/config/theming.html
    default = "default"
    neutral = "neutral"
    dark = "dark"
    forest = "forest"
    base = "base"


class SyrenkaConfig(ABC):
    def __init__(self):
        super().__init__()
        self.config = {}

    def to_code(self):
        ret = ["config:"]
        for key, val in self.config.items():
            ret.append(f"  {key}: {val}")
        return ret

    def set(self, name, value) -> Self:
        if type(name) is not str:
            return self

        if value:
            self.config[name] = value
        else:
            self.config.pop(name, None)

        return self

    def theme(self, theme_name: ThemeNames | str) -> Self:
        return self.set("theme", theme_name)


class SyrenkaGeneratorBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def to_code(
        self, indent_level: int = 0, indent_base: str = "    "
    ) -> Iterable[str]:
        pass


def dunder_name(s: str) -> bool:
    return s.startswith("__") and s.endswith("__")


def under_name(s: str) -> bool:
    return s.startswith("_") and s.endswith("_")


def neutralize_under(s: str) -> str:
    return s.replace("_", "\\_")

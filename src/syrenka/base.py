from abc import ABC, abstractmethod
from collections.abc import Iterable

from typing import Tuple


class StringHelper:
    @staticmethod
    def indent(
        level: int, increment: int = 0, indent_base: str = "    "
    ) -> Tuple[int, str]:
        level += increment
        return level, indent_base * level


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

"""syrenka base"""

from abc import ABC, abstractmethod
from io import TextIOBase
from typing import Tuple, Union

try:
    from enum import StrEnum
except ImportError:
    # backward compatibility for python <3.11
    from strenum import StrEnum

DEFAULT_INDENT = "    "


def get_indent(
    level: int, increment: int = 0, indent_base: str = "    "
) -> Tuple[int, str]:
    """returns indent string"""
    level += increment
    return level, indent_base * level


class ThemeNames(StrEnum):
    """
    Theme names in mermaid

    For actual list see: https://mermaid.js.org/config/theming.html
    """

    DEFAULT = "default"
    NEUTRAL = "neutral"
    DARK = "dark"
    FOREST = "forest"
    BASE = "base"


class SyrenkaConfig(ABC):
    """Syrenka class for mermaid config"""

    def __init__(self):
        super().__init__()
        self.config = {}

    def to_code(self, file: TextIOBase):
        """generate mermaid code for Frontmatter"""
        file.write("config:\n")
        for key, val in self.config.items():
            file.write(f"  {key}: {val}\n")

    def set(self, name, value):
        """set value in config"""
        if isinstance(name, str):
            return self

        if value:
            self.config[name] = value
        else:
            self.config.pop(name, None)

        return self

    def theme(self, theme_name: Union[ThemeNames, str]):
        """sets theme"""
        return self.set("theme", theme_name)


class SyrenkaGeneratorBase(ABC):
    """Base class for Syrenka code generators"""

    @abstractmethod
    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        """This method implementation should write output to passed file."""


def dunder_name(s: str) -> bool:
    """checks if it is dunder name - double underscore start and end"""
    return s.startswith("__") and s.endswith("__")


def under_name(s: str) -> bool:
    """checks if the name starts and ends with underscore"""
    return s.startswith("_") and s.endswith("_")


def neutralize_under(s: str) -> str:
    """neutralizes underscores for mermaid diagram"""
    return s.replace("_", "\\_")

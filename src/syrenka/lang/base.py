from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Union

try:
    from enum import StrEnum
except ImportError:
    # backward compatibility for python <3.11
    from strenum import StrEnum


class LangAccess(StrEnum):
    PUBLIC = "+"
    PROTECTED = "#"
    PRIVATE = "-"


@dataclass
class LangVar:
    """Variable identifier and type"""

    name: str
    typee: Union[str, None] = None


@dataclass
class LangAttr:
    name: str
    typee: Union[str, None] = None
    access: LangAccess = LangAccess.PUBLIC


@dataclass
class LangFunction:
    """Function entry"""

    ident: LangVar
    args: list[LangVar] = field(default_factory=list)
    access: LangAccess = LangAccess.PUBLIC


class LangClass(ABC):
    @abstractmethod
    def is_enum(self) -> bool:
        pass

    @abstractmethod
    def _parse(self, force: bool = True):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def namespace(self) -> str:
        pass

    @abstractmethod
    def functions(self) -> Iterable[LangFunction]:
        pass

    @abstractmethod
    def attributes(self) -> Iterable[LangVar]:
        pass

    @abstractmethod
    def parents(self) -> Iterable[str]:
        pass


class LangAnalysis(ABC):
    def __call__(self, *args, **kwds):
        super().__init__()

    @staticmethod
    @abstractmethod
    def handles(obj) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def create_lang_class(obj) -> LangClass:
        pass


LANG_ANALYSIS = []


def register_lang_analysis(cls, last=False):
    if cls in LANG_ANALYSIS:
        raise ValueError("Unexpected second register")
    if last:
        LANG_ANALYSIS.append(cls)
    else:
        LANG_ANALYSIS.insert(0, cls)

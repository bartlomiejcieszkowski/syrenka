from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Iterable
from enum import StrEnum


class LangAccess(StrEnum):
    Public = "+"
    Protected = "#"
    Private = "-"


@dataclass
class LangVar:
    """Variable identifier and type"""

    name: str
    typee: str = None


@dataclass
class LangAttr:
    name: str
    typee: str = None
    access: LangAccess = LangAccess.Public


@dataclass
class LangFunction:
    """Function entry"""

    ident: LangVar
    args: list[LangVar] = field(default_factory=list)
    access: LangAccess = LangAccess.Public


class LangClass(ABC):
    def __init__(self):
        super().__init__()

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
    global LANG_ANALYSIS
    if cls in LANG_ANALYSIS:
        raise Exception("Unexpected second register")
    if last:
        LANG_ANALYSIS.append(cls)
    else:
        LANG_ANALYSIS.insert(0, cls)

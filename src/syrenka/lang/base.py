"""syrenka.lang.base"""

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
    """Attributes"""

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
    """base class for lang class parsing"""

    @abstractmethod
    def is_enum(self) -> bool:
        """this method should return true if this class is an enum"""
        pass

    @abstractmethod
    def _parse(self, force: bool = True):
        """this method should implement parsing of class"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """this method should return name of class"""
        pass

    @property
    @abstractmethod
    def namespace(self) -> str:
        """this method should return namespace of class"""
        pass

    @abstractmethod
    def functions(self) -> Iterable[LangFunction]:
        """this method should return functions in class"""
        pass

    @abstractmethod
    def attributes(self) -> Iterable[LangVar]:
        """this method should return attributes in class"""
        pass

    @abstractmethod
    def parents(self) -> Iterable[str]:
        """this method should return parents of class"""
        pass


class LangAnalysis(ABC):
    @staticmethod
    @abstractmethod
    def handles(obj) -> bool:
        """this method should return True only if the class provides capabilities for language analysis of given obj"""
        pass

    @staticmethod
    @abstractmethod
    def create_lang_class(obj) -> Union[LangClass, None]:
        """this method should create object that is instance of LangClass"""
        pass


LANG_ANALYSIS = []


def register_lang_analysis(cls, last=False):
    """registers globally lang analysis class"""
    if cls in LANG_ANALYSIS:
        raise ValueError("Unexpected second register")
    if last:
        LANG_ANALYSIS.append(cls)
    else:
        LANG_ANALYSIS.insert(0, cls)

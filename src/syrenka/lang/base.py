from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Iterable


@dataclass
class LangVar:
    """Variable identifier and type"""

    name: str
    typee: str = None


@dataclass
class LangFunction:
    """Function entry"""

    ident: LangVar
    args: list[LangVar] = field(default_factory=list)


class LangClass(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _parse(self, force: bool = True):
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def functions(self) -> Iterable[LangFunction]:
        pass

    @abstractmethod
    def attributes(self) -> Iterable[LangVar]:
        pass

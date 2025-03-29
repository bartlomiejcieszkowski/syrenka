from abc import ABC, abstractmethod
from typing import Iterable


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
    def functions(self) -> Iterable[tuple[str, Iterable[str]]]:
        pass

    @abstractmethod
    def attributes(self):
        pass

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Tuple
from types import ModuleType
import importlib
from inspect import isclass, ismodule
import sys


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


def isbuiltin_module(module: ModuleType) -> bool:
    return module.__name__ in sys.builtin_module_names


def dunder_name(s: str) -> bool:
    return s.startswith("__") and s.endswith("__")


def under_name(s: str) -> bool:
    return s.startswith("_") and s.endswith("_")


def neutralize_under(s: str) -> str:
    return s.replace("_", "\\_")


def _classes_in_module(module: ModuleType, nested: bool = True):
    module_path = Path(module.__file__).parent

    classes = []
    module_names = []
    stash = [module]

    while len(stash):
        m = stash.pop()
        module_names.append(m.__name__)

        # print(m)
        for name in dir(m):
            if dunder_name(name):
                continue

            attr = getattr(m, name)
            if ismodule(attr):
                if not nested:
                    continue

                if not hasattr(attr, "__file__"):
                    # eg. sys
                    continue

                if module_path not in Path(attr.__file__).parents:
                    continue

                stash.append(attr)

            if not isclass(attr):
                continue

            classes.append(attr)

    classes[:] = [classe for classe in classes if classe.__module__ in module_names]

    return classes


def classes_in_module(module_name, nested: bool = True):
    module = importlib.import_module(module_name)
    return _classes_in_module(module, nested)


def generate_class_list_from_module(module_name, starts_with=""):
    module = importlib.import_module(module_name)
    classes = []
    for name in dir(module):
        if dunder_name(name):
            continue
        print(f"\t{name}")
        if name.startswith(starts_with):
            attr = getattr(module, name)
            if isclass(attr):
                classes.append()

    return classes

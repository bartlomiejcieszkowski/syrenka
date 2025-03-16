from abc import ABC, abstractmethod
from typing import Iterable, Tuple
from types import MethodType, ModuleType, FunctionType
import builtins
import importlib
from inspect import isclass, ismodule


class StringHelper:
    @staticmethod
    def indent(level: int, increment: int=0, indent_base: str = "    ") -> Tuple[int, str]:
        level += increment
        return level, indent_base * level
    

class SyrenkaGeneratorBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        pass


# type(s).__name__ in dir(builtins)
def is_builtin(t):
    builtin = getattr(builtins, t.__name__, None)

    # This one is only needed if we want to safeguard against typee = None
    if not builtin:
        return False
    
    return builtin is t

def dunder_name(s: str) -> bool:
    return s.startswith("__") and s.endswith("__")

def under_name(s: str) -> bool:
    return s.startswith("_") and s.endswith("_")

def neutralize_under(s: str) -> str:
    return s.replace("_", "\\_")

def _classes_in_module(module: ModuleType, nested: bool=True):
    classes = []
    stash = [module]

    while len(stash):
        m = stash.pop()
        # print(m)
        for name in dir(m):
            if dunder_name(name):
                continue

            attr = getattr(m, name)
            if ismodule(attr):
                if nested and attr.__name__.startswith(module.__name__):
                    stash.append(attr)
                continue

            if not isclass(attr):
                continue

            classes.append(attr)

    return classes



def classes_in_module(module_name, nested: bool=True):
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
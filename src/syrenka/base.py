from abc import ABC, abstractmethod
from typing import Iterable, Tuple
import builtins
import importlib


class StringHelper:
    @staticmethod
    def indent(level: int, increment: int=0, indent_base: str = "    ") -> Tuple[int, str]:
        level += increment
        return level, indent_base * level
    

class MermaidGeneratorBase(ABC):
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

def generate_class_list_from_module(module_name, starts_with=""):
    module = importlib.import_module(module_name)
    classes = []
    for name in dir(module):
        print(f"\t{name}")
        if name.startswith(starts_with):
            classes.append(getattr(module, name))

    return classes
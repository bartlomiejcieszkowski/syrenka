from typing import Iterable, Tuple
from abc import ABC, abstractmethod
from enum import Enum

import builtins
import importlib

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

class StringHelper:
    @staticmethod
    def indent(level: int, increment: int, indent_base: str = "    ") -> Tuple[int, str]:
        level += increment
        return level, indent_base * level

class MermaidGeneratorBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def to_code(self) -> Iterable[str]:
        pass

class MermaidClass(MermaidGeneratorBase):
    def __init__(self, cls, skip_underscores: bool=True):
        super().__init__()
        self.cls = cls
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(self):
        ret = []
        t = self.cls

        print(f"{t.__name__} builtin? {is_builtin(t)}")

        level, indent = StringHelper.indent(0, 1)

        # class <name> {
        ret.append(f"{indent}class {t.__name__}{'{'}")

        level, indent = StringHelper.indent(level, 1)

        methods = []

        for x in dir(t):
            if self.skip_underscores and x.startswith("__"):
                continue
            attr = getattr(t, x)
            if callable(attr):
                if not hasattr(attr, "__code__"):
                    # case of <class 'method_descriptor'>, built-in methods
                    # __code__ approach can't be used for them
                    # heuristic with doc string..
                    if hasattr(attr, "__doc__"):
                        d = attr.__doc__
                        # print(f"{attr.__name__} ", d)
                        try:
                            args_text = d[d.index('(')+1:d.index(')')]
                            # this is naive
                            # str.center.__doc__
                            # 'Return a centered string of length width.\n\nPadding is done using the specified fill character (default is a space).'
                        except ValueError:
                            # substring not found
                            args_text = ""    
                    else:
                        args_text = ""
                    methods.append(f"{indent}+{attr.__name__}({args_text})")
                else:
                    args = attr.__code__.co_varnames[:attr.__code__.co_argcount]
                    local_variables = attr.__code__.co_varnames[attr.__code__.co_argcount:]
                    args_str = ', '.join(args)
                    methods.append(f"{indent}+{x}({args_str})")

        ret.extend(methods)
        level, indent = StringHelper.indent(level, -1)

        ret.append(f"{indent}{'}'}")

        return ret


class MermaidClassDiagram(MermaidGeneratorBase):
    def __init__(self, title: str=""):
        super().__init__()
        self.title = title
        self.classes : Iterable[MermaidGeneratorBase] = []
        pass

    def to_code(self) -> Iterable[str]:
        mcode = [
            "---",
            f"title: {self.title}",
            "---",
            "classDiagram",
        ]

        for mclass in self.classes:
            mcode.extend(mclass.to_code())

        return mcode
    
    def add_class(self, cls):
        self.classes.append(MermaidClass(cls))

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)



class MermaidFlowchartDirection(Enum):
    TopToBottom = "TB"
    LeftToRight = "LR"
    BottomToTop = "BT"
    RightToLeft = "RL"


class MermaidFlowchart(MermaidGeneratorBase):
    def __init__(self, title: str, direction: MermaidFlowchartDirection):
        super().__init__()
        self.title = title
        self.direction = direction

    def to_code(self) -> Iterable[str]:
        mcode = [
            "---",
            f"title: {self.title}",
            "---",
            f"flowchart {self.direction.value}",
        ]

        return mcode
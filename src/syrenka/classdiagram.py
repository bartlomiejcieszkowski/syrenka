from .base import (
    SyrenkaGeneratorBase,
    StringHelper,
    dunder_name,
    under_name,
    neutralize_under,
)
from enum import Enum
from inspect import isclass
from collections.abc import Iterable

from syrenka.lang.python import PythonClass

SKIP_OBJECT = True


class SyrenkaEnum(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool = True):
        super().__init__()
        self.cls = cls
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(
        self, indent_level: int = 0, indent_base: str = "    "
    ) -> Iterable[str]:
        ret = []
        t = self.cls

        indent_level, indent = StringHelper.indent(
            indent_level, indent_base=indent_base
        )

        # class <name> {
        ret.append(f"{indent}class {t.__name__}{'{'}")
        indent_level, indent = StringHelper.indent(indent_level, 1, indent_base)

        ret.append(indent + "<<enumeration>>")

        for x in dir(t):
            if dunder_name(x):
                continue

            attr = getattr(t, x)
            if type(attr) is t:
                # enum values are instances of this enum
                ret.append(indent + x)

        # TODO: what about methods in enum?
        indent_level, indent = StringHelper.indent(indent_level, -1, indent_base)
        ret.append(f"{indent}{'}'}")

        return ret


# TODO: self variables.. how to get them
# 1. Instantiate class, and see whats in the object - this is bad idea, as you need to call constructor of random classes
# 2. class.__init__.__code__.co_names - you get all the names used.. but these are all, so you get also super and called method names..
#    and they are pure strings
# 3. ast - load file content into ast, find this class, find __init__
# 3.1. Get first arg in __init__ - yes, it should be self, but it can be something else, cause why not
# 3.1. go over __init__ body, find assignments with name same as first arg of init,  Attribute(value=Name(id='self', ctx=Load()), attr='cls', ctx=Store())]


class SyrenkaClass(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool = True):
        super().__init__()
        self.lang_class = PythonClass(cls)
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(
        self, indent_level: int = 0, indent_base: str = "    "
    ) -> Iterable[str]:
        ret = []

        indent_level, indent = StringHelper.indent(
            indent_level, indent_base=indent_base
        )

        # class <name> {
        ret.append(f"{indent}class {self.lang_class.name}{'{'}")

        indent_level, indent = StringHelper.indent(indent_level, 1, indent_base)

        for attr in self.lang_class.attributes():
            typee_str = f"{attr.typee} " if attr.typee else ""
            ret.append(f"{indent}{attr.access}{typee_str}{attr.name}")

        for lang_fun in self.lang_class.functions():
            args_text = ""
            if lang_fun.args:
                for arg in lang_fun.args:
                    if arg.typee:
                        args_text += f"{arg.typee} {arg.name}, "
                        continue

                    args_text += arg.name + ", "
                # remove last ", "
                args_text = args_text[:-2]

            function_sanitized = lang_fun.ident.name
            if under_name(function_sanitized):
                function_sanitized = neutralize_under(function_sanitized)

            ret.append(f"{indent}{lang_fun.access}{function_sanitized}({args_text})")

        indent_level, indent = StringHelper.indent(indent_level, -1, indent_base)

        ret.append(f"{indent}{'}'}")

        # inheritence
        bases = getattr(self.lang_class.cls, "__bases__", None)
        if bases:
            for base in bases:
                if SKIP_OBJECT and base.__name__ == "object":
                    continue
                ret.append(f"{indent}{base.__name__} <|-- {self.lang_class.name}")
                # print(f"{t.__name__} base: {base.__name__}")

        return ret


def get_syrenka_cls(cls):
    if not isclass(cls):
        return None

    if issubclass(cls, Enum):
        return SyrenkaEnum

    return SyrenkaClass


class SyrenkaClassDiagram(SyrenkaGeneratorBase):
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.unique_classes = {}
        self.classes: Iterable[SyrenkaGeneratorBase] = []
        pass

    def to_code(
        self, indent_level: int = 0, indent_base: str = "    "
    ) -> Iterable[str]:
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)
        mcode = [
            indent + "---",
            f"{indent}title: {self.title}",
            indent + "---",
            indent + "classDiagram",
        ]

        for mclass in self.classes:
            mcode.extend(mclass.to_code(indent_level + 1, indent_base))

        return mcode

    # TODO: check cls file origin
    def add_class(self, cls):
        if cls not in self.unique_classes:
            syrenka_cls = get_syrenka_cls(cls)
            if syrenka_cls:
                self.classes.append(syrenka_cls(cls=cls))
            self.unique_classes[cls] = None

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)

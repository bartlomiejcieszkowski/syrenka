from .base import (
    SyrenkaGeneratorBase,
    StringHelper,
    dunder_name,
    under_name,
    neutralize_under,
)
from enum import Enum
from inspect import isclass, getfullargspec, isbuiltin, ismethoddescriptor
from typing import Iterable

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


class SyrenkaClass(SyrenkaGeneratorBase):
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

        methods = []

        for x in dir(t):
            is_init = False
            if self.skip_underscores and dunder_name(x):
                is_init = x == "__init__"
                if not is_init:
                    continue

            attr = getattr(t, x)
            if callable(attr):
                fullarg = None

                if isbuiltin(attr):
                    # print(f"builtin: {t.__name__}.{x} - skip - fails getfullargspec")
                    continue

                if ismethoddescriptor(attr):
                    # print(f"methoddescriptor: {t.__name__}.{x} - skip - fails getfullargspec")
                    f = getattr(attr, "__func__", None)
                    # print(f)
                    # print(attr)
                    # print(dir(attr))
                    if f is None:
                        # <slot wrapper '__init__' of 'object' objects>
                        continue

                    # <bound method _SpecialGenericAlias.__init__ of typing.MutableSequence>
                    fullarg = getfullargspec(f)
                    print(f"bound fun {f.__name__}: {fullarg}")

                if fullarg is None:
                    fullarg = getfullargspec(attr)
                args_text = "("
                arg_text_list = []
                for arg in fullarg.args:
                    arg_text = arg

                    if arg in fullarg.annotations:
                        type_hint = fullarg.annotations.get(arg)
                        if hasattr(type_hint, "__qualname__"):
                            arg_text = type_hint.__qualname__ + " " + arg_text
                        else:
                            # print(f"no __qualname__ - {type_hint} - type: {type(type_hint)}")
                            pass
                        # extract type hint

                    arg_text_list.append(arg_text)

                args_text = ", ".join(arg_text_list)
                methods.append(
                    f"{indent}+{neutralize_under(x) if under_name(x) else x}({args_text})"
                )

        ret.extend(methods)
        indent_level, indent = StringHelper.indent(indent_level, -1, indent_base)

        ret.append(f"{indent}{'}'}")

        # inheritence
        bases = getattr(t, "__bases__", None)
        if bases:
            for base in bases:
                if SKIP_OBJECT and base.__name__ == "object":
                    continue
                ret.append(f"{indent}{base.__name__} <|-- {t.__name__}")
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

from .base import SyrenkaGeneratorBase, StringHelper, is_builtin, dunder_name, under_name, neutralize_under
from inspect import isclass
from typing import Iterable

SKIP_OBJECT = True

class SyrenkaClass(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool=True):
        super().__init__()
        self.cls = cls
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        ret = []
        t = self.cls
        #if not callable(t):
        if not isclass(t):
            return ret

        indent_level, indent = StringHelper.indent(indent_level, indent_base=indent_base)

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
                        except (ValueError, AttributeError):
                            # substring not found
                            # index found nothing
                            args_text = ""    
                    else:
                        args_text = ""
                    if under_name(x):
                        x = neutralize_under(x)
                    methods.append(f"{indent}+{x}({args_text})")
                else:
                    if is_init:
                        for var in attr.__code__.co_names:
                            if var not in ["super", "__init__"]:
                                v = var
                                v = neutralize_under(var) if under_name(var) else var
                                methods.append(f"{indent}-{v}")

                    args = attr.__code__.co_varnames[:attr.__code__.co_argcount]
                    # local_variables = attr.__code__.co_varnames[attr.__code__.co_argcount:]
                    args_str = ', '.join(args)
                    if under_name(x):
                        x = neutralize_under(x)
                    methods.append(f"{indent}+{x}({args_str})")

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
                #print(f"{t.__name__} base: {base.__name__}")

        return ret


class SyrenkaClassDiagram(SyrenkaGeneratorBase):
    def __init__(self, title: str=""):
        super().__init__()
        self.title = title
        self.unique_classes = {}
        self.classes : Iterable[SyrenkaGeneratorBase] = []
        pass

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)
        mcode = [
            indent + "---",
            f"{indent}title: {self.title}",
            indent + "---",
            indent + "classDiagram",
        ]

        for mclass in self.classes:
            mcode.extend(mclass.to_code(indent_level+1, indent_base))

        return mcode
    
    def add_class(self, cls):
        if cls not in self.unique_classes:
            self.classes.append(SyrenkaClass(cls))
            self.unique_classes[cls] = None

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)



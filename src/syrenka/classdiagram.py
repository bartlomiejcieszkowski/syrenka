from .base import SyrenkaGeneratorBase, StringHelper, is_builtin
from typing import Iterable

class SyrenkaClass(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool=True):
        super().__init__()
        self.cls = cls
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        ret = []
        t = self.cls

        indent_level, indent = StringHelper.indent(indent_level, indent_base=indent_base)

        # class <name> {
        ret.append(f"{indent}class {t.__name__}{'{'}")

        indent_level, indent = StringHelper.indent(indent_level, 1, indent_base)

        methods = []

        for x in dir(t):
            if self.skip_underscores and x.startswith("__") and not x == "__init__":
                continue

            is_init = x is "__init__"
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
                    methods.append(f"{indent}+{attr.__name__}({args_text})")
                else:
                    if is_init:
                        for var in attr.__code__.co_names:
                            if var not in ["super", "__init__"]:
                                methods.append(f"{indent}-{var}")

                    args = attr.__code__.co_varnames[:attr.__code__.co_argcount]
                    # local_variables = attr.__code__.co_varnames[attr.__code__.co_argcount:]
                    args_str = ', '.join(args)
                    methods.append(f"{indent}+{x}({args_str})")

        ret.extend(methods)
        indent_level, indent = StringHelper.indent(indent_level, -1, indent_base)

        ret.append(f"{indent}{'}'}")

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
            print(mclass.cls)
            mcode.extend(mclass.to_code(indent_level+1, indent_base))

        return mcode
    
    def add_class(self, cls):
        if cls not in self.unique_classes:
            self.classes.append(SyrenkaClass(cls))
            self.unique_classes[cls] = None

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)



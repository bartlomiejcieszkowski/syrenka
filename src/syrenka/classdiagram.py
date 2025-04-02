from .base import (
    SyrenkaConfig,
    SyrenkaGeneratorBase,
    get_indent,
    dunder_name,
    under_name,
    neutralize_under,
)
from enum import Enum
from inspect import isclass
from collections.abc import Iterable

from syrenka.lang.python import PythonClass
from copy import deepcopy

from io import TextIOBase

SKIP_BASES = True
SKIP_BASES_LIST = ["object", "ABC"]


class SyrenkaEnum(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool = True):
        super().__init__()
        self.cls = cls
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    @property
    def name(self) -> str:
        return self.cls.__name__

    @property
    def namespace(self) -> str:
        return self.cls.__module__

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        t = self.cls

        indent_level, indent = get_indent(indent_level, indent_base=indent_base)

        # class <name> {
        file.writelines([indent, "class ", t.__name__, "{\n"])
        indent_level, indent = get_indent(indent_level, 1, indent_base)

        file.writelines([indent, "<<enumeration>>", "\n"])

        for x in dir(t):
            if dunder_name(x):
                continue

            attr = getattr(t, x)
            if type(attr) is t:
                # enum values are instances of this enum
                file.writelines([indent, x, "\n"])

        # TODO: what about methods in enum?
        indent_level, indent = get_indent(indent_level, -1, indent_base)
        file.writelines([indent, "}\n"])

    def to_code_inheritance(
        self, file, indent_level: int = 0, indent_base: str = "    "
    ):
        pass


class SyrenkaClass(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool = True):
        super().__init__()
        self.lang_class = PythonClass(cls)
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    @property
    def name(self) -> str:
        return self.lang_class.name

    @property
    def namespace(self) -> str:
        return self.lang_class.namespace

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        indent_level, indent = get_indent(indent_level, indent_base=indent_base)

        # class <name> {
        file.writelines([indent, "class ", self.lang_class.name, "{\n"])

        indent_level, indent = get_indent(indent_level, 1, indent_base)

        for attr in self.lang_class.attributes():
            typee_str = f"{attr.typee} " if attr.typee else ""
            file.writelines([indent, attr.access, typee_str, attr.name, "\n"])

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

            file.writelines(
                [indent, lang_fun.access, function_sanitized, "(", args_text, ")\n"]
            )

        indent_level, indent = get_indent(indent_level, -1, indent_base)

        file.writelines([indent, "}\n"])

    def to_code_inheritance(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        indent_level, indent = get_indent(indent_level, indent_base=indent_base)

        # inheritence
        bases = getattr(self.lang_class.cls, "__bases__", None)
        if bases:
            for base in bases:
                if SKIP_BASES and base.__name__ in SKIP_BASES_LIST:
                    continue
                file.writelines(
                    [indent, base.__name__, " <|-- ", self.lang_class.name, "\n"]
                )


def get_syrenka_cls(cls):
    if not isclass(cls):
        return None

    if issubclass(cls, Enum):
        return SyrenkaEnum

    return SyrenkaClass


class SyrenkaClassDiagramConfig(SyrenkaConfig):
    CLASS_CONFIG_DEFAULTS = {"hideEmptyMembersBox": "true"}

    def __init__(self):
        super().__init__()
        class_config = deepcopy(SyrenkaClassDiagramConfig.CLASS_CONFIG_DEFAULTS)
        self.class_config = {"class": class_config}

    def to_code(self, file: TextIOBase):
        super().to_code(file)
        for key, val in self.class_config.items():
            file.write(f"  {key}:\n")
            for subkey, subval in val.items():
                file.write(f"    {subkey}: {subval}\n")


class SyrenkaClassDiagram(SyrenkaGeneratorBase):
    def __init__(
        self,
        title: str = "",
        config: SyrenkaClassDiagramConfig = SyrenkaClassDiagramConfig(),
    ):
        super().__init__()
        self.title = title
        self.namespaces_with_classes: dict[str, dict[str, SyrenkaGeneratorBase]] = {}
        self.unique_classes = {}
        self.config = config

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ) -> Iterable[str]:
        indent_level, indent = get_indent(indent_level, 0, indent_base)

        # Frontmatter
        file.writelines(
            [
                indent + "---\n",
                f"{indent}title: {self.title}\n",
            ]
        )

        self.config.to_code(file)

        file.writelines([indent, "---", "\n"])
        file.writelines([indent, "classDiagram", "\n"])

        # for mclass in self.classes:
        #    mcode.extend(mclass.to_code(indent_level + 1, indent_base))

        for namespace, classes in self.namespaces_with_classes.items():
            file.writelines([indent, "namespace ", namespace, "{\n"])
            indent_level, indent = get_indent(indent_level, 1, indent_base)
            for _, mclass in classes.items():
                mclass.to_code(
                    file=file, indent_level=indent_level, indent_base=indent_base
                )
            indent_level, indent = get_indent(indent_level, -1, indent_base)
            file.writelines([indent, "}", "\n"])

        file.write("%% inheritance\n")
        for classes in self.namespaces_with_classes.values():
            for _, mclass in classes.items():
                mclass.to_code_inheritance(
                    file=file, indent_level=indent_level, indent_base=indent_base
                )

    # TODO: check cls file origin
    def add_class(self, cls):
        # TODO: There is a corner-case of same class name but different namespace, it will clash on diagram
        if cls not in self.unique_classes:
            syrenka_cls = get_syrenka_cls(cls)
            if syrenka_cls:
                class_obj = syrenka_cls(cls=cls)
                if class_obj.namespace not in self.namespaces_with_classes:
                    self.namespaces_with_classes[class_obj.namespace] = {}

                if (
                    class_obj.name
                    not in self.namespaces_with_classes[class_obj.namespace]
                ):
                    self.namespaces_with_classes[class_obj.namespace][
                        class_obj.name
                    ] = class_obj
            self.unique_classes[cls] = None

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)

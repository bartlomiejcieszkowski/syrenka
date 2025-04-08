from syrenka.base import (
    SyrenkaConfig,
    SyrenkaGeneratorBase,
    get_indent,
    under_name,
    neutralize_under,
)
from collections.abc import Iterable

from syrenka.lang import LangAnalyst
from copy import deepcopy

from io import TextIOBase


class SyrenkaClass(SyrenkaGeneratorBase):
    def __init__(self, cls, skip_underscores: bool = True):
        super().__init__()
        self.lang_class = LangAnalyst.create_lang_class(cls)
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

        if self.lang_class.is_enum():
            file.writelines([indent, "<<enumeration>>", "\n"])
            for enum_value in self.lang_class.info["enum"]:
                file.writelines([indent, enum_value, "\n"])
            file.write("\n")

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
        self,
        file: TextIOBase,
        indent_level: int = 0,
        indent_base: str = "    ",
        valid_classes: dict[str, None] = None,
    ):
        if self.lang_class.is_enum():
            return

        indent_level, indent = get_indent(indent_level, indent_base=indent_base)

        for parent in self.lang_class.parents():
            if valid_classes:
                if parent in valid_classes:
                    file.writelines(
                        [indent, parent, " <|-- ", self.lang_class.name, "\n"]
                    )
                continue
            file.writelines([indent, parent, " <|-- ", self.lang_class.name, "\n"])


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
        imported_classes: bool = False,
    ):
        super().__init__()
        self.title = title
        self.namespaces_with_classes: dict[str, dict[str, SyrenkaGeneratorBase]] = {}
        self.unique_classes = {}
        self.config = config
        self.imported_classes = imported_classes

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

        for namespace, classes in self.namespaces_with_classes.items():
            if namespace:
                file.writelines([indent, "namespace ", namespace, "{\n"])
                indent_level, indent = get_indent(indent_level, 1, indent_base)
            for _, mclass in classes.items():
                mclass.to_code(
                    file=file, indent_level=indent_level, indent_base=indent_base
                )
            if namespace:
                indent_level, indent = get_indent(indent_level, -1, indent_base)
                file.writelines([indent, "}", "\n"])

        file.write("%% inheritance\n")
        valid_classes = None
        if not self.imported_classes:
            # if we don't want imported classes we pass current unique classes to filter inheritance
            # this will make class diagram look cleaner, but might hide details
            valid_classes = self.unique_classes

        for classes in self.namespaces_with_classes.values():
            for _, mclass in classes.items():
                mclass.to_code_inheritance(
                    file=file,
                    indent_level=indent_level,
                    indent_base=indent_base,
                    valid_classes=valid_classes,
                )

    # TODO: check cls file origin
    def add_class(self, cls):
        # TODO: There is a corner-case of same class name but different namespace, it will clash on diagram
        class_obj = SyrenkaClass(cls=cls)
        if class_obj.name in self.unique_classes:
            return

        if class_obj.namespace not in self.namespaces_with_classes:
            self.namespaces_with_classes[class_obj.namespace] = {}

        if class_obj.name not in self.namespaces_with_classes[class_obj.namespace]:
            self.namespaces_with_classes[class_obj.namespace][class_obj.name] = (
                class_obj
            )
        self.unique_classes[class_obj.name] = None

    def add_classes(self, classes):
        for cls in classes:
            self.add_class(cls)

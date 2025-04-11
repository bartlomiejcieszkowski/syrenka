from collections.abc import Iterable
from inspect import isclass, ismodule
from pathlib import Path
from types import ModuleType
import importlib
import ast
from enum import Enum
from dataclasses import dataclass

import sys
from inspect import getfullargspec, isbuiltin, ismethoddescriptor

from syrenka.base import dunder_name

from syrenka.lang.base import (
    LangAccess,
    LangAnalysis,
    LangAttr,
    LangClass,
    LangVar,
    LangFunction,
    register_lang_analysis,
)

import logging

logger = logging.getLogger(__name__)


SKIP_BASES = True
SKIP_BASES_LIST = ["object", "ABC"]


@dataclass(frozen=True)
class PythonAstModuleParams:
    ast_module: ast.Module
    filepath: Path


@dataclass(frozen=True)
class PythonAstClassParams:
    ast_class: ast.ClassDef
    filepath: Path
    root: Path


class PythonAstClass(LangClass):
    def __init__(self, params):
        super().__init__()
        self.cls: ast.ClassDef = params.ast_class
        self.filepath = params.filepath
        self.root = params.root
        self.info = {}
        self.parsed = False
        self._namespace = None

    def _parse(self, force: bool = False):
        if self.parsed and not force:
            return

        self.info.clear()
        functions = []
        attributes = []

        attribute_assign = []

        is_dataclass = False
        if self.cls.decorator_list:
            for decorator in self.cls.decorator_list:
                # might be dataclass
                if type(decorator) is ast.Call:
                    if decorator.func.id == "dataclass":
                        is_dataclass = True
                elif type(decorator) is ast.Name:
                    if decorator.id == "dataclass":
                        is_dataclass = True

        for ast_node in self.cls.body:
            if type(ast_node) is ast.Assign:
                if type(ast_node.value) not in [ast.Constant, ast.Name]:
                    logger.debug(
                        f"ast.Asign - discarded ({type(ast_node.value)}) {ast_node.value = }"
                    )
                    continue

                for target in ast_node.targets:
                    if type(target) is ast.Name:
                        break

                if type(target) is not ast.Name:
                    logger.debug(f"ast.Asign - discarded ({type(target)}) {target = }")
                    continue

                attribute_assign.append(target.id)
                continue

            if is_dataclass and type(ast_node) is ast.AnnAssign:
                # eg. name: str
                # ast_node.annotation # ast.Name
                attributes.append(
                    LangAttr(
                        name=ast_node.target.id,
                        typee=None,  # todo from annotation
                        access=PythonModuleAnalysis.get_access_from_name(
                            ast_node.target.id
                        ),
                    )
                )

            if type(ast_node) is not ast.FunctionDef:
                # print(ast_node)
                continue

            args_list = []
            for ast_arg in ast_node.args.args:
                if ast_arg.annotation:
                    if type(ast_arg.annotation) is ast.BinOp:
                        # theme_name: ThemeNames | str
                        # TODO
                        args_list.append(LangVar(ast_arg.arg))
                        continue

                    if type(ast_arg.annotation) is ast.Subscript:
                        # text: Union[str, None] = None,
                        # TODO
                        args_list.append(LangVar(ast_arg.arg))
                        continue

                    if type(ast_arg.annotation) is ast.Name:
                        args_list.append(LangVar(ast_arg.arg, ast_arg.annotation.id))
                        continue

                    if type(ast_arg.annotation) is ast.Attribute:
                        typee = (
                            ast_arg.annotation.value.id + "." + ast_arg.annotation.attr
                        )
                        args_list.append(LangVar(ast_arg.arg, typee))
                        continue

                    raise Exception("TODO not handled")

                lv = LangVar(ast_arg.arg)

                args_list.append(lv)

            lf = LangFunction(
                ident=LangVar(ast_node.name),
                args=args_list,
                access=PythonModuleAnalysis.get_access_from_name(ast_node.name),
            )

            functions.append(lf)

            if ast_node.name == "__init__":
                attributes.extend(PythonModuleAnalysis.get_assign_attributes(ast_node))

        self.info["functions"] = functions
        self.info["attributes"] = attributes

        is_enum = any(map(lambda x: "enum" in x.lower(), self.parents()))

        if is_enum:
            self.info["enum"] = attribute_assign
        elif attribute_assign:
            # ATM we dont care about class attributes
            pass

        self.parsed = True

    def is_enum(self) -> bool:
        self._parse()
        return "enum" in self.info

    @property
    def name(self):
        return self.cls.name

    @property
    def namespace(self):
        if self._namespace is not None:
            return self._namespace

        if self.filepath.is_relative_to(self.root):
            relative = self.filepath.relative_to(self.root)

            ns = []
            # -1 to skip '.'
            for i in range(0, len(relative.parts) - 1):
                ns.append(relative.parts[i])

            if not dunder_name(relative.stem):
                ns.append(relative.stem)

            self._namespace = ".".join(ns)
        else:
            self._namespace = ""

        return self._namespace

    def functions(self):
        self._parse()
        return self.info["functions"]

    def attributes(self):
        self._parse()
        return self.info["attributes"]

    def parents(self) -> Iterable[str]:
        parents = []
        for base in self.cls.bases:
            parents.append(base.id)

        return parents


@dataclass(frozen=True)
class PythonClassParams:
    cls: object


class PythonClass(LangClass):
    def __init__(self, params: PythonClassParams):
        super().__init__()
        self.cls = params.cls
        self.parsed = False
        self.info = {}
        self._skip_dunder_names = True

    def _parse(self, force: bool = False):
        if self.parsed and not force:
            return

        self.info.clear()

        functions = []
        attributes = []
        enum_values = []

        for x in dir(self.cls):
            is_init = False
            if self._skip_dunder_names and dunder_name(x):
                is_init = x == "__init__"
                if not is_init:
                    continue

            attr = getattr(self.cls, x)
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
                    # print(f"bound fun {f.__name__}: {fullarg}")

                if fullarg is None:
                    fullarg = getfullargspec(attr)

                args_list = None
                if fullarg.args:
                    args_list = []
                    for arg in fullarg.args:
                        arg_type = None

                        if arg in fullarg.annotations:
                            type_hint = fullarg.annotations.get(arg)
                            if hasattr(type_hint, "__qualname__"):
                                arg_type = type_hint.__qualname__

                        args_list.append(LangVar(arg, arg_type))

                if is_init:
                    function_body = PythonModuleAnalysis.get_ast_function(
                        attr.__code__.co_filename, attr.__code__.co_firstlineno
                    )
                    if function_body:
                        attributes.extend(
                            PythonModuleAnalysis.get_assign_attributes(function_body)
                        )

                # TODO: type hint for return type???
                functions.append(
                    LangFunction(
                        LangVar(x),
                        args_list,
                        PythonModuleAnalysis.get_access_from_name(x),
                    )
                )
            elif type(attr) is self.cls:
                # enum values are instances of this enum
                enum_values.append(x)

        self.info["functions"] = functions
        self.info["attributes"] = attributes
        self.info["enum"] = enum_values

        self.parsed = True

    def is_enum(self) -> bool:
        self._parse()
        return issubclass(self.cls, Enum)

    @property
    def name(self):
        return self.cls.__name__

    @property
    def namespace(self):
        return self.cls.__module__

    def functions(self):
        self._parse()
        return self.info["functions"]

    def attributes(self):
        self._parse()
        return self.info["attributes"]

    def parents(self) -> Iterable[str]:
        parents = []
        bases = getattr(self.cls, "__bases__", None)
        if bases:
            for base in bases:
                if SKIP_BASES and base.__name__ in SKIP_BASES_LIST:
                    continue
                parents.append(base.__name__)

        return parents


class PythonModuleAnalysis(LangAnalysis):
    ast_cache: dict[Path, ast.Module] = {}

    @staticmethod
    def handles(obj) -> bool:
        return type(obj) in [PythonAstClassParams, PythonClassParams]

    @staticmethod
    def create_lang_class(obj) -> LangClass:
        if type(obj) is PythonAstClassParams:
            return PythonAstClass(obj)

        if type(obj) is PythonClassParams:
            return PythonClass(obj)

        return None

    @staticmethod
    def isbuiltin_module(module: ModuleType) -> bool:
        return module.__name__ in sys.builtin_module_names

    @staticmethod
    def _classes_in_module(
        module: ModuleType, nested: bool = True
    ) -> Iterable[PythonClassParams]:
        module_path = Path(module.__file__).parent

        classes = []
        module_names = []
        stash = [module]

        while len(stash):
            m = stash.pop()
            if m.__name__ in module_names:
                # circular?
                continue

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

                    if attr.__file__:
                        # namespace might have None for file, eg folder without __init__.py
                        if module_path not in Path(attr.__file__).parents:
                            continue

                    stash.append(attr)

                if not isclass(attr):
                    continue

                classes.append(attr)

        class_params = []
        for cls in classes:
            if cls.__module__ in module_names:
                class_params.append(PythonClassParams(cls=cls))

        return class_params

    @staticmethod
    def classes_in_module(
        module_name, nested: bool = True
    ) -> Iterable[PythonClassParams]:
        module = importlib.import_module(module_name)
        return PythonModuleAnalysis._classes_in_module(module, nested)

    PYTHON_EXT = [".py"]

    @staticmethod
    def classes_in_path(
        path: Path, root: Path | None = None, recursive: bool = True
    ) -> Iterable[PythonAstClassParams]:
        if root is None:
            root = path

        ast_modules = []

        paths = [path]

        while paths:
            p = paths.pop(0)
            if p.is_dir():
                for child in p.iterdir():
                    paths.append(child)
            elif p.is_file() and p.suffix in PythonModuleAnalysis.PYTHON_EXT:
                ast_modules.append(
                    PythonAstModuleParams(
                        ast_module=PythonModuleAnalysis.get_ast(p), filepath=p
                    )
                )
            else:
                # print(f"skipped: {p}", sys.stderr)
                pass

        return PythonModuleAnalysis.get_classes_from_ast(ast_modules, root)

    @staticmethod
    def get_classes_from_ast(
        ast_modules: Iterable[PythonAstModuleParams],
        root: Path,
    ) -> Iterable[PythonAstClassParams]:
        class_params = []
        # this is shallow, we dont take into account classes in classes
        for params in ast_modules:
            for ast_node in params.ast_module.body:
                if type(ast_node) is ast.ClassDef:
                    class_params.append(
                        PythonAstClassParams(
                            ast_class=ast_node, filepath=params.filepath, root=root
                        )
                    )
                else:
                    # print(ast_node)
                    pass
        return class_params

    @staticmethod
    def get_ast(filename: Path | str):
        if type(filename) is str:
            filename = Path(filename)

        if not filename.exists():
            return None

        ast_module = PythonModuleAnalysis.ast_cache.get(filename, None)
        if ast_module is None:
            with filename.open("r", encoding="utf-8") as f:
                ast_module = ast.parse(f.read(), str(filename.name))
            PythonModuleAnalysis.ast_cache[filename] = ast_module

        return ast_module

    @staticmethod
    def get_ast_node(filename: Path | str, firstlineno, ast_type):
        ast_module = PythonModuleAnalysis.get_ast(filename)

        ast_nodes = [ast_module]
        while ast_node := ast_nodes.pop():
            if type(ast_node) is ast_type and ast_node.lineno == firstlineno:
                break

            for child in ast_node.body:
                if child.lineno <= firstlineno and child.end_lineno >= firstlineno:
                    ast_nodes.append(child)
                    break

        return ast_node

    @staticmethod
    def get_ast_function(filename: Path | str, firstlineno) -> ast.FunctionDef:
        return PythonModuleAnalysis.get_ast_node(filename, firstlineno, ast.FunctionDef)

    @staticmethod
    def get_access_from_name(name):
        if name[0] == "_":
            if not dunder_name(name):
                return LangAccess.Private

        return LangAccess.Public

    @staticmethod
    def get_assign_attributes(ast_function: ast.FunctionDef) -> Iterable[LangAttr]:
        attributes = {}
        for entry in ast_function.body:
            if type(entry) is not ast.Assign:
                continue

            for target in entry.targets:
                if type(target) is ast.Attribute:
                    break

            if type(target) is not ast.Attribute:
                continue

            attributes[target.attr] = LangAttr(
                name=target.attr,
                typee=None,
                access=PythonModuleAnalysis.get_access_from_name(target.attr),
            )

        return attributes.values()


register_lang_analysis(PythonModuleAnalysis, last=True)

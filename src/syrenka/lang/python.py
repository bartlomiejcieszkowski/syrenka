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
    globals_as_class: bool = False


@dataclass(frozen=True)
class PythonAstClassParams:
    ast_class: ast.ClassDef
    filepath: Path
    root: Path
    module_name: str | None


class PythonAstClass(LangClass):
    def __init__(self, params):
        super().__init__()
        self.cls: ast.ClassDef = params.ast_class
        self.filepath = params.filepath
        self.root = params.root
        self.module_name = params.module_name
        self.info = {}
        self.parsed = False
        self._namespace = None

        # TODO: Should be done properly as some PythonAstModule, but it works, refactor later
        if type(self.cls) is ast.ClassDef:
            self._name = self.cls.name
        else:
            self._name = "_globals_"

    def _parse(self, force: bool = False):
        if self.parsed and not force:
            return

        self.info.clear()
        functions = []
        attributes = []

        attribute_assign = []

        is_dataclass = False
        if hasattr(self.cls, "decorator_list") and self.cls.decorator_list:
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
                # if type(ast_node.value) not in [ast.Constant, ast.Name, ast.Call]:
                #     logger.debug(
                #         f"ast.Asign - discarded ({type(ast_node.value)}) {ast_node.value = }"
                #     )
                #     continue

                for target in ast_node.targets:
                    if type(target) is not ast.Name:
                        logger.debug(
                            f"ast.Assign - discarded ({type(target)}) {target = }"
                        )
                        continue

                    attribute_assign.append(
                        LangAttr(
                            name=target.id,
                            typee=None,
                            access=PythonModuleAnalysis.get_access_from_name(target.id),
                        ),
                    )

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
        return self._name

    @property
    def namespace(self):
        if self._namespace is not None:
            return self._namespace

        ns = []
        if self.module_name:
            ns.append(self.module_name)

        if self.filepath.is_relative_to(self.root):
            relative = self.filepath.relative_to(self.root)

            # -1 to skip '.'
            for i in range(0, len(relative.parts) - 1):
                ns.append(relative.parts[i])

            if not dunder_name(relative.stem):
                ns.append(relative.stem)

        self._namespace = ".".join(ns)

        return self._namespace

    def functions(self):
        self._parse()
        return self.info["functions"]

    def attributes(self):
        self._parse()
        return self.info["attributes"]

    def parents(self) -> Iterable[str]:
        parents = []
        if hasattr(self.cls, "bases"):
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
                enum_values.append(
                    LangAttr(
                        name=x,
                        typee=None,
                        access=PythonModuleAnalysis.get_access_from_name(x),
                    )
                )

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
        path: Path,
        module_name: str | None = None,
        recursive: bool = True,
        detect_project_dir: bool = True,
        exclude: Iterable[str] | None = None,
        only: Iterable[str] | None = None,
        globals_as_class: bool = False,
    ) -> Iterable[PythonAstClassParams]:
        root = path

        if path.is_dir():
            if detect_project_dir:
                maybe_src = path / "src"
                if maybe_src.exists() and maybe_src.is_dir():
                    root = path = maybe_src

        ast_modules = []

        paths = [path]

        while paths:
            p = paths.pop(0)
            if p.is_dir():
                for child in p.iterdir():
                    paths.append(child)
            elif p.is_file() and p.suffix in PythonModuleAnalysis.PYTHON_EXT:
                rel_path = p.relative_to(root).as_posix()
                append = True

                if only and any(map(lambda x: not rel_path.startswith(x), only)):
                    append = False

                if exclude and any(map(lambda x: rel_path.startswith(x), exclude)):
                    append = False

                logger.debug(f"{rel_path=}, {append=}")
                if append:
                    ast_modules.append(
                        PythonAstModuleParams(
                            ast_module=PythonModuleAnalysis.get_ast(p),
                            filepath=p,
                            globals_as_class=globals_as_class,
                        )
                    )
            else:
                # print(f"skipped: {p}", sys.stderr)
                pass

        return PythonModuleAnalysis.get_classes_from_ast(ast_modules, root, module_name)

    @staticmethod
    def get_classes_from_ast(
        ast_modules: Iterable[PythonAstModuleParams],
        root: Path,
        module_name: str | None,
    ) -> Iterable[PythonAstClassParams]:
        class_params = []
        # this is shallow, we dont take into account classes in classes
        for params in ast_modules:
            found_non_class = False
            for ast_node in params.ast_module.body:
                logger.debug(f"{params.filepath.as_posix()}: {ast_node}")
                if type(ast_node) is ast.ClassDef:
                    class_params.append(
                        PythonAstClassParams(
                            ast_class=ast_node,
                            filepath=params.filepath,
                            root=root,
                            module_name=module_name,
                        )
                    )
                elif params.globals_as_class and not found_non_class:
                    if type(ast_node) not in [ast.Import, ast.ImportFrom]:
                        found_non_class = True
                    # TODO
                    pass
            if params.globals_as_class and found_non_class:
                logger.debug(
                    f"{params.filepath.as_posix()}: adding _globals_ pseudo-class"
                )
                class_params.append(
                    PythonAstClassParams(
                        ast_class=params.ast_module,
                        filepath=params.filepath,
                        root=root,
                        module_name=module_name,
                    )
                )
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

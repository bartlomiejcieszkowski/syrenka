from abc import ABC
from collections.abc import Iterable
from inspect import isclass, ismodule
from pathlib import Path
from types import ModuleType
import importlib
import ast

import sys
from inspect import getfullargspec, isbuiltin, ismethoddescriptor

from syrenka.base import dunder_name

from syrenka.lang.base import LangAccess, LangAttr, LangClass, LangVar, LangFunction


class PythonClass(LangClass):
    def __init__(self, cls):
        super().__init__()
        self.cls = cls
        self.parsed = False
        self.info = {}
        self.skip_underscores = True

    def _parse(self, force: bool = False):
        if self.parsed and not force:
            return

        self.info.clear()

        functions = []
        attributes = {}

        for x in dir(self.cls):
            is_init = False
            if self.skip_underscores and dunder_name(x):
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
                        # TODO get self
                        attributes = PythonModuleAnalysis.get_assign_attributes(
                            function_body
                        )

                # TODO: type hint for return type???
                functions.append(
                    LangFunction(
                        LangVar(x),
                        args_list,
                        PythonModuleAnalysis.get_access_from_name(x),
                    )
                )

        self.info["functions"] = functions
        self.info["attributes"] = attributes
        self.parsed = True

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


class PythonModuleAnalysis(ABC):
    ast_cache: dict[Path, ast.Module] = {}

    @staticmethod
    def isbuiltin_module(module: ModuleType) -> bool:
        return module.__name__ in sys.builtin_module_names

    @staticmethod
    def _classes_in_module(module: ModuleType, nested: bool = True):
        module_path = Path(module.__file__).parent

        classes = []
        module_names = []
        stash = [module]

        while len(stash):
            m = stash.pop()
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

        classes[:] = [classe for classe in classes if classe.__module__ in module_names]

        return classes

    @staticmethod
    def classes_in_module(module_name, nested: bool = True):
        module = importlib.import_module(module_name)
        return PythonModuleAnalysis._classes_in_module(module, nested)

    @staticmethod
    def generate_class_list_from_module(module_name, starts_with=""):
        module = importlib.import_module(module_name)
        classes = []
        for name in dir(module):
            if dunder_name(name):
                continue
            print(f"\t{name}")
            if name.startswith(starts_with):
                attr = getattr(module, name)
                if isclass(attr):
                    classes.append()

        return classes

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
    def get_ast_function(filename: Path | str, firstlineno):
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
                if type(target) is not ast.Attribute:
                    # TODO: is this possible?
                    continue

            attributes[target.attr] = LangAttr(
                name=target.attr,
                typee=None,
                access=PythonModuleAnalysis.get_access_from_name(target.attr),
            )

        return attributes.values()

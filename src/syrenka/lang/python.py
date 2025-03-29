from abc import ABC
from inspect import isclass, ismodule
from pathlib import Path
from types import ModuleType
import importlib

import sys
from inspect import getfullargspec, isbuiltin, ismethoddescriptor

from syrenka.base import dunder_name

from syrenka.lang.base import LangClass


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
        attributes = []

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

                arg_text_list = None
                if fullarg.args:
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

                functions.append((x, arg_text_list))

        self.info["functions"] = functions
        self.info["attributes"] = attributes
        self.parsed = True

    @property
    def name(self):
        return self.cls.__name__

    def functions(self):
        self._parse()
        return self.info["functions"]

    def attributes(self):
        self._parse()
        return self.info["attributes"]


class ModuleAnalysis(ABC):
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
        return ModuleAnalysis._classes_in_module(module, nested)

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

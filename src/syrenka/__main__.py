import os
import sys
import argparse
import syrenka
from syrenka.lang.python import PythonModuleAnalysis

from pathlib import Path


def _import_module(args):
    classes = PythonModuleAnalysis.classes_in_module(args.module, nested=True)

    class_diagram = syrenka.SyrenkaClassDiagram()
    class_diagram.add_classes(classes)
    class_diagram.to_code(file=sys.stdout)


def _class_diagram(args):
    classes = PythonModuleAnalysis.classes_in_path(Path(args.path), recursive=True)

    class_diagram = syrenka.SyrenkaClassDiagram()
    class_diagram.add_classes(classes)
    class_diagram.to_code(file=sys.stdout)


def _main():
    prog = os.path.basename(sys.argv[0])
    if prog.endswith("__main__.py"):
        prog = "python -m syrenka"

    ap = argparse.ArgumentParser(prog=prog, allow_abbrev=False)

    subparsers = ap.add_subparsers(dest="cmd")
    class_diagram = subparsers.add_parser(
        "class", aliases=["c", "classdiagram", "class_diagram"]
    )
    class_diagram.add_argument("path", help="folder/file with source")
    class_diagram.set_defaults(func=_class_diagram)

    import_module = subparsers.add_parser("import_module")
    import_module.add_argument("module", help="module name")
    import_module.set_defaults(func=_import_module)

    args = ap.parse_args()
    if args.cmd is None:
        ap.print_usage()
        return -1

    return args.func(args)


if __name__ == "__main__":
    ret = _main()
    sys.exit(ret)

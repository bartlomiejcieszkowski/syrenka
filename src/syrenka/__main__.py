import sys
import argparse
import syrenka
from syrenka.base import classes_in_module


def _class_diagram(args):
    classes = classes_in_module(args.module, args.nested)

    class_diagram = syrenka.SyrenkaClassDiagram()
    class_diagram.add_classes(classes)

    for line in class_diagram.to_code():
        print(line)


def _main():
    ap = argparse.ArgumentParser(allow_abbrev=False)

    subparsers = ap.add_subparsers()
    class_diagram = subparsers.add_parser(
        "class", aliases=["c", "classdiagram", "class_diagram"]
    )
    class_diagram.add_argument("module")
    class_diagram.add_argument("-n", "--nested", action="store_true")
    class_diagram.set_defaults(func=_class_diagram)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    ret = _main()
    sys.exit(ret)

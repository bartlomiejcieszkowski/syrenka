from typing import Tuple

class StringHelper:
    @staticmethod
    def indent(level: int, increment: int, indent_base: str = "    ") -> Tuple[int, str]:
        level += increment
        return level, indent_base * level

class MermaidClassDiagram:
    def __init__(self, c, skip_underscores: bool=True):
        self.c = c
        self.indent = 4 * " "
        self.skip_underscores = skip_underscores

    def to_code(self):
        ret = []
        t = type(self.c)

        level, indent = StringHelper.indent(0, 1)

        # class <name> {
        ret.append(f"{indent}class {t.__name__}{'{'}")

        level, indent = StringHelper.indent(level, 1)

        methods = []

        for x in dir(t):
            if self.skip_underscores and x.startswith("__"):
                continue
            if callable(getattr(t, x)):
                methods.append(f"{indent}+{x}(?)")

        ret.extend(methods)
        level, indent = StringHelper.indent(level, -1)

        ret.append(f"{indent}{'}'}")

        return ret



if __name__ == "__main__":
    test = "test"
    mm = MermaidClassDiagram(test)
    r = mm.to_code()
    for l in r:
        print(l)
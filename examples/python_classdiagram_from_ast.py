"""Example SyrenkaClassDiagram with ast backend."""

# from io import StringIO
import sys
from pathlib import Path

from syrenka.base import ThemeNames
from syrenka.classdiagram import SyrenkaClassDiagram, SyrenkaClassDiagramConfig
from syrenka.lang.python import PythonModuleAnalysis

class_diagram = SyrenkaClassDiagram(
    "syrenka class diagram", SyrenkaClassDiagramConfig().theme(ThemeNames.NEUTRAL)
)
class_diagram.add_classes(
    PythonModuleAnalysis.classes_in_path(
        Path(__file__).parent.parent / "src"
    )  # , recursive==True)
)

# file can be anything that implements TextIOBase
# out = StringIO() # string buffer in memory
out = sys.stdout  # stdout
# out = open("syrenka.md", "w") # write it to file

class_diagram.to_code(file=out)

# StringIO
# out.seek(0)
# print(out.read())

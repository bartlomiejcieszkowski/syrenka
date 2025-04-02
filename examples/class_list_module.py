from syrenka.classdiagram import SyrenkaClassDiagram, SyrenkaClassDiagramConfig
from syrenka.base import ThemeNames
from syrenka.lang.python import PythonModuleAnalysis

# from io import StringIO
import sys

class_diagram = SyrenkaClassDiagram(
    "syrenka class diagram", SyrenkaClassDiagramConfig().theme(ThemeNames.neutral)
)
class_diagram.add_classes(
    PythonModuleAnalysis.classes_in_module(module_name="syrenka", nested=True)
)

# file can be anything that implements TextIOBase
# out = StringIO() # string buffer in memory
out = sys.stdout  # stdout
# out = open("syrenka.md", "w") # write it to file

class_diagram.to_code(file=out)

# StringIO
# out.seek(0)
# print(out.read())

import syrenka
from syrenka.lang.python import PythonModuleAnalysis

class_diagram = syrenka.SyrenkaClassDiagram("syrenka class diagram")
class_diagram.add_classes(
    PythonModuleAnalysis.classes_in_module(module_name="syrenka", nested=True)
)

for line in class_diagram.to_code():
    print(line)

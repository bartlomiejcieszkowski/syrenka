import syrenka
from syrenka.lang.python import ModuleAnalysis

class_diagram = syrenka.SyrenkaClassDiagram("syrenka class diagram")
class_diagram.add_classes(
    ModuleAnalysis.classes_in_module(module_name="syrenka", nested=True)
)

for line in class_diagram.to_code():
    print(line)

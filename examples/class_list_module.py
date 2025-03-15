import syrenka
from syrenka.base import generate_class_list_from_module

class_diagram  = syrenka.SyrenkaClassDiagram("syrenka class diagram")
class_diagram.add_classes(generate_class_list_from_module(module_name="syrenka", starts_with="Syrenka"))

for line in class_diagram.to_code():
    print(line)
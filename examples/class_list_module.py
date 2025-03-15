import syrenka

class_diagram  = syrenka.SyrenkaClassDiagram("syrenka class diagram")
class_diagram.add_classes(syrenka.generate_class_list_from_module(module_name="syrenka", starts_with="Mermaid")

for line in class_diagram.to_code():
    print(line)
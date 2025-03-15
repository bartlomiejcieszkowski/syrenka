import syrenka
from syrenka.base import generate_class_list_from_module
from syrenka.flowchart import SyrenkaFlowchart, FlowchartDirection



if __name__ == "__main__":
    flowchart = SyrenkaFlowchart("", FlowchartDirection.LeftToRight)
    for l in flowchart.to_code():
        print(l)

    class_list = generate_class_list_from_module("syrenka", "Mermaid")

    mm = syrenka.SyrenkaClassDiagram()
    
    mm.add_classes(class_list)
    #mm.add_class(str)
    
    r = mm.to_code()
    for l in r:
        print(l)
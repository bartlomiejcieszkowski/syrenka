import syrenka

if __name__ == "__main__":
    flowchart = syrenka.MermaidFlowchart("", syrenka.MermaidFlowchartDirection.LeftToRight)
    for l in flowchart.to_code():
        print(l)

    class_list = syrenka.generate_class_list_from_module("syrenka", "Mermaid")

    mm = syrenka.MermaidClassDiagram()
    
    mm.add_classes(class_list)
    #mm.add_class(str)
    
    r = mm.to_code()
    for l in r:
        print(l)
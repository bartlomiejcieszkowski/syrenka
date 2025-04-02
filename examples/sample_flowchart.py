import syrenka.flowchart as sf
import sys

# flowchart TB
#     c1-->a2
#     subgraph one
#     a1-->a2
#     end
#     subgraph two
#     b1-->b2
#     end
#     subgraph three
#     c1-->c2
#     end
#     one --> two
#     three --> two
#     two --> c2
# from https://mermaid.js.org/syntax/flowchart.html

# TODO: Edges

flowchart = sf.SyrenkaFlowchart(
    "",
    sf.FlowchartDirection.TopToBottom,
    nodes=[
        sf.Subgraph(
            "one",
            nodes=[
                sf.Node("a1"),
                sf.Node("a2"),
            ],
        ),
        sf.Subgraph(
            "two",
            nodes=[
                sf.Node("b1"),
                sf.Node("b2"),
            ],
        ),
        sf.Subgraph(
            "three",
            nodes=[
                sf.Node("c1"),
                sf.Node("c2"),
            ],
        ),
    ],
)

flowchart.connect_by_id("c1", "a2").connect_by_id("a1", "a2")
flowchart.connect_by_id("b1", "b2").connect_by_id("c1", "c2")
flowchart.connect_by_id("one", "two").connect_by_id("three", "two").connect_by_id(
    "two", "c2"
)

# beware, it looks like in mermaid order of the edge changes how its rendered
# if i declare edge c1 --> a2 before and after subgraphs, it gets drawn totally different
flowchart.to_code(file=sys.stdout)

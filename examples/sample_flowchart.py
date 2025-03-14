import syrenka.flowchart as sf

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

flowchart = sf.MermaidFlowchart("", sf.MermaidFlowchartDirection.TopToBottom,
    nodes=[
        sf.Node("c1"),
        sf.Node("a2"),
        sf.Subgraph("one", nodes=[
            sf.Node("a1")
        ]),
        sf.Subgraph("two", nodes=[
            sf.Node("b1"),
            sf.Node("b2"),
        ]),
        sf.Subgraph("three", nodes=[
            sf.Node("c1"),
            sf.Node("c2"),
        ])
    ]
    )

for line in flowchart.to_code():
    print(line)
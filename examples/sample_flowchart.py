"""Example SyrenkaFlowchart usage."""

from io import StringIO
from pathlib import Path

import syrenka.flowchart as sf
from syrenka.generate import generate_diagram_image

flowchart = sf.SyrenkaFlowchart(
    "",
    sf.FlowchartDirection.TOP_TO_BOTTOM,
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
            direction=sf.FlowchartDirection.LEFT_TO_RIGHT,
            nodes=[
                sf.Node("b1"),
                sf.Node("b2"),
            ],
        ),
        sf.Subgraph(
            "three",
            direction=sf.FlowchartDirection.BOTTOM_TO_TOP,
            nodes=[
                sf.Node("c1"),
                sf.Node("c2"),
            ],
        ),
    ],
)

flowchart.connect_by_id("c1", "a2").connect_by_id("a1", "a2")
flowchart.connect_by_id("b1", "b2").connect_by_id("c1", "c2")
flowchart.connect_by_id("one", "two").connect_by_id("three", "two").connect_by_id("two", "c2")

out = StringIO()
flowchart.to_code(file=out)

print(out.getvalue())

generate_diagram_image(out.getvalue(), Path("out.svg"), overwrite=True)

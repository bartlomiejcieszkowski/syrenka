"""Example Simple SyrenkaFlowchart."""

import sys

import syrenka.flowchart as sf

fl = sf.SyrenkaFlowchart(
    title="Simple Flowchart", direction=sf.FlowchartDirection.TOP_TO_BOTTOM
)
fl.add(sf.Node(identifier="1", text="First"))
sub = sf.Subgraph(identifier="s", text="Subgraph")
sub.add(sf.Node(identifier="2", text="Second"))
sub.add(sf.Node(identifier="3", text="Third"))
fl.add(sub)
fl.add(sf.Node(identifier="4", text="Fourth"))

fl.connect_by_id("1", "2")
fl.connect_by_id(source_id="2", target_id="3", edge_type=sf.EdgeType.DOTTED_LINK)
fl.connect_by_id("3", "4").connect_by_id("4", "s", sf.EdgeType.THICK_LINK)

fl.to_code(file=sys.stdout)

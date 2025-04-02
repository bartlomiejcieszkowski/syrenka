import syrenka.flowchart as sf
import sys

fl = sf.SyrenkaFlowchart(
    title="Simple Flowchart", direction=sf.FlowchartDirection.TopToBottom
)
fl.add(sf.Node(id="1", text="First"))
sub = sf.Subgraph(id="s", text="Subgraph")
sub.add(sf.Node(id="2", text="Second"))
sub.add(sf.Node(id="3", text="Third"))
fl.add(sub)
fl.add(sf.Node(id="4", text="Fourth"))

fl.connect_by_id("1", "2")
fl.connect_by_id(source_id="2", target_id="3", edge_type=sf.EdgeType.DottedLink)
fl.connect_by_id("3", "4").connect_by_id("4", "s", sf.EdgeType.ThickLink)

fl.to_code(file=sys.stdout)

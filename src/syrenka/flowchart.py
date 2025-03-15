from collections import OrderedDict
from .base import SyrenkaGeneratorBase, StringHelper

from enum import Enum
from typing import Iterable, Self, Union
from collections.abc import MutableSequence

def get_title(title: str):
    return [
        "---",
        f"title: {title}",
        "---",
    ]

class FlowchartDirection(Enum):
    TopToBottom = "TB"
    LeftToRight = "LR"
    BottomToTop = "BT"
    RightToLeft = "RL"

class NodeShape(Enum):
    Default = "[]"
    RoundEdges = "()"
    StadiumShapedNode = "([])"
    SubroutineShape = "[[]]"
    CylindricalShape = "[()]"
    Circle = "(())"
    AssymetricShape = ">]"
    Rhombus = "{}"
    HexagonNode = "{{}}"
    Parallelogram = "[//]"
    Trapezoid = "[/\\]"
    TrapezoidAlt = "[\\/]"
    DoubleCircle = "((()))"

    @staticmethod
    def get_edges(node_shape):
        v = node_shape.value
        half = len(v) // 2
        return node_shape.value[:half], node_shape.value[half:]
    
# TODO New shape method in v11.3.0+

class Node(SyrenkaGeneratorBase):
    def __init__(self, id: str, text: Union[str, None]=None, shape: NodeShape=NodeShape.Default):
        self.id = id
        self.text = text
        self.shape = shape

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)
        e_open, e_close = NodeShape.get_edges(self.shape)
        text = self.text
        if self.shape is not NodeShape.Default and not text:
            text = self.id

        if self.text:
            return [f'{indent}{self.id}{e_open}"{self.text}"{e_close}']

        return [f"{indent}{self.id}"]

class EdgeType(Enum):
    ArrowEdge = "-->"
    OpenLink = "---"
    DottedLink = "-.->"
    ThickLink = "==>"
    InvisibleLink = "~~~"
    # New arrow types
    CircleEdge = "--o"
    CrossEdge = "--x"
    # Multi directional arrows
    MultiCircleEdge = "o--o"
    MultiArrowEdge = "<-->"
    MultiCrossEdge = "x--x"


# Animation?

class Edge(SyrenkaGeneratorBase):
    def __init__(self, edge_type: EdgeType=EdgeType.ArrowEdge, text: str|None = None, source: Node|None = None, target: Node|None = None):
        self.id = None
        self.edge_type = edge_type
        self.text = text
        self.source = source
        self.target = target

    def valid(self) -> bool:
        return self.source and self.target
    
    def to_code(self, indent_level = 0, indent_base = "    "):
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)
        edge_id = f"{self.id}@" if self.id else ""
        return [f"{indent}{self.source.id} {edge_id}{self.edge_type.value} {self.target.id}"]

class Subgraph(Node):
    def __init__(self, id: str, text: str|None=None, direction: FlowchartDirection=FlowchartDirection.TopToBottom, nodes: MutableSequence[Node]=[]):
        super().__init__(id=id, text=text, shape=NodeShape.Default)
        self.edges = []
        self.direction = direction
        self.nodes_dict = OrderedDict()
        self.subgraphs_dict = OrderedDict()
        for node in nodes:
            if isinstance(node, Subgraph):
                self.subgraphs_dict[node.id] = node
            self.nodes_dict[node.id] = node
            # TODO: what if someone updates id in Node?

    def get_node_by_id(self, id: str) -> Node|None:
        node = self.nodes_dict.get(id, None)
        if node:
            return node
        
        # search subgraphs
        for subgraph in self.subgraphs_dict.values():
            node = subgraph.get_node_by_id(id)
            if node:
                return node
        
        return None
        raise KeyError(f"No node by id: {id}")

    def add(self, node: Node) -> Self:
        self.nodes_dict[node.id] = node
        return self

    def remove(self, node: Node, exception_if_not_exists: bool=False) -> Self:
        if exception_if_not_exists:
            self.nodes_dict.pop(node.id)
        else:
            self.nodes_dict.pop(node.id, None)

        return self

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)

        mcode = [f"{indent}subgraph {self.id}"]

        for node in self.nodes_dict.values():
            mcode.extend(node.to_code(indent_level, indent_base))

        mcode.append(indent + "end")
        return mcode

class SyrenkaFlowchart(Subgraph):
    def __init__(self, title: str, direction: FlowchartDirection, nodes: MutableSequence[Node]=None):
        super().__init__(id=title, direction=direction, nodes=nodes)

    def connect(self, source: Node, target: Node, edge_type: EdgeType=EdgeType.ArrowEdge) -> Self:
        self.edges.append(Edge(edge_type, "text opt", source=source, target=target))
        # for method-chaining
        return self

    def connect_by_id(self, source_id: str, target_id: str, edge_type: EdgeType=EdgeType.ArrowEdge) -> Self:
        source = self.get_node_by_id(source_id)
        target = self.get_node_by_id(target_id)

        return self.connect(source, target)

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        indent_level, indent = StringHelper.indent(indent_level, 0, indent_base)
        mcode = [
            f"{indent}flowchart {self.direction.value}"
        ]

        if self.id:
            mcode = get_title(self.id) + mcode

        # easiest workaround for edges going BEHIND subgraphs
        # if i place edges AFTER subgraphs, some might get rendered under subgraph..
        for edge in self.edges:
            mcode.extend(edge.to_code(indent_level+1, indent_base))

        for node in self.nodes_dict.values():
            mcode.extend(node.to_code(indent_level+1, indent_base))



        return mcode
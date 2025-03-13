from .base import MermaidGeneratorBase

from enum import Enum
from typing import Iterable, Union
from collections.abc import MutableSequence

class MermaidFlowchartDirection(Enum):
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
    Trapezoid = "[/\]"
    TrapezoidAlt = "[\/]"
    DoubleCircle = "((()))"

    @staticmethod
    def get_edges(node_shape):
        v = node_shape.value
        half = len(v) // 2
        return node_shape.value[:half], node_shape.value[half:]
    
# TODO New shape method in v11.3.0+

class Node(MermaidGeneratorBase):
    def __init__(self, id: str, text: Union[str, None]=None, shape: NodeShape=NodeShape.Default):
        self.id = id
        self.text = text
        self.shape = shape

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        e_open, e_close = NodeShape.get_edges(self.shape)
        text = self.text
        if self.shape is not NodeShape.Default and not text:
            text = self.id

        if self.text:
            return f'{id}{e_open}"{self.text}"{e_close}'

        return f"{id}"

class Edge:
    def __init__(self, typee, text: str|None = None, source: Node|None = None, target: Node|None = None):
        self.type = typee
        self.text = text
        self.source = None
        self.target = None 

    def valid(self) -> bool:
        # TODO is oroboros connection allowed?
        return self.source and self.target and self.source is not self.target

class Subgraph(Node):
    def __init__(self, id: str, text: str|None=None,  nodes: MutableSequence[Node]=[]):
        super().__init__(id=id, text=text, shape=NodeShape.Default)
        self.nodes: MutableSequence[Node] = nodes
        # TODO: could do sanity check for duplicates here

    def add(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)

    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        mcode = ""

class MermaidFlowchart(Subgraph):
    def __init__(self, title: str, direction: MermaidFlowchartDirection, nodes: MutableSequence[Node]=None):
        super().__init__(id=title, nodes=nodes)
        self.direction = direction



    def to_code(self, indent_level: int=0, indent_base: str="    ") -> Iterable[str]:
        mcode = [
            "---",
            f"title: {self.id}",
            "---",
            f"flowchart {self.direction.value}",
        ]

        return mcode
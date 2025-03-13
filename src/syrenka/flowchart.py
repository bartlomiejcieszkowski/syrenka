from .base import MermaidGeneratorBase

from enum import Enum
from typing import Iterable, Union

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

class MermaidFlowchartNode:
    def __init__(self, id: str, text: Union[str, None]=None, shape: NodeShape=NodeShape.Default):
        self.id = id
        self.text = text
        self.shape = shape

    def to_code(self) -> Iterable[str]:
        e_open, e_close = NodeShape.get_edges(self.shape)
        text = self.text
        if self.shape is not NodeShape.Default and not text:
            text = self.id

        if self.text:
            return f'{id}{e_open}"{self.text}"{e_close}'

        return f"{id}"

class Subgraph:
    def __init__(self, nodes: Iterable[MermaidFlowchartNode]=[]):
        self.nodes = nodes

class MermaidFlowchart(MermaidGeneratorBase):
    def __init__(self, title: str, direction: MermaidFlowchartDirection):
        super().__init__()
        self.title = title
        self.direction = direction



    def to_code(self) -> Iterable[str]:
        mcode = [
            "---",
            f"title: {self.title}",
            "---",
            f"flowchart {self.direction.value}",
        ]

        return mcode
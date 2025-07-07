from collections import OrderedDict
from enum import Enum
from io import TextIOBase
from typing import Iterable, Union

from .base import SyrenkaGeneratorBase, get_indent


def get_title(title: str):
    return [
        "---\n",
        f"title: {title}\n",
        "---\n",
    ]


class FlowchartDirection(Enum):
    TOP_TO_BOTTOM = "TB"
    LEFT_TO_RIGHT = "LR"
    BOTTOM_TO_TOP = "BT"
    RIGHT_TO_LEFT = "RL"


class NodeShape(Enum):
    DEFAULT = "[]"
    ROUND_EDGES = "()"
    STADIUM_SHAPED_NODE = "([])"
    SUBROUTINE_SHAPE = "[[]]"
    CYLINDRICAL_SHAPE = "[()]"
    CIRCLE = "(())"
    ASSYMETRIC_SHAPE = ">]"
    RHOMBUS = "{}"
    HEXAGON_NODE = "{{}}"
    PARALLELOGRAM = "[//]"
    TRAPEZOID = "[/\\]"
    TRAPEZOID_ALT = "[\\/]"
    DOUBLE_CIRCLE = "((()))"

    @staticmethod
    def get_edges(node_shape):
        v = node_shape.value
        half = len(v) // 2
        return node_shape.value[:half], node_shape.value[half:]


# TODO New shape method in v11.3.0+


class Node(SyrenkaGeneratorBase):
    def __init__(
        self,
        identifier: str,
        text: Union[str, None] = None,
        shape: NodeShape = NodeShape.DEFAULT,
    ):
        self.identifier = identifier
        self.text = text
        self.shape = shape

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        indent_level, indent = get_indent(indent_level, 0, indent_base)
        e_open, e_close = NodeShape.get_edges(self.shape)
        text = self.text
        if self.shape is not NodeShape.DEFAULT and not text:
            text = self.identifier

        if self.text:
            file.writelines(
                [indent, self.identifier, e_open, '"', self.text, '"', e_close, "\n"]
            )
        else:
            file.writelines([indent, self.identifier, "\n"])


class EdgeType(Enum):
    """Mermaid edge type (links between nodes)

    For reference see: https://mermaid.js.org/syntax/flowchart.html#links-between-nodes"""

    ARROW_EDGE = "-->"
    OPEN_LINK = "---"
    DOTTED_LINK = "-.->"
    THICK_LINK = "==>"
    INVISIBLE_LINK = "~~~"
    # New arrow types
    CIRCLE_EDGE = "--o"
    CROSS_EDGE = "--x"
    # Multi directional arrows
    MULTI_CIRCLE_EDGE = "o--o"
    MULTI_ARROW_EDGE = "<-->"
    MULTI_CROSS_EDGE = "x--x"


# Animation?


class Edge(SyrenkaGeneratorBase):
    def __init__(
        self,
        edge_type: EdgeType = EdgeType.ARROW_EDGE,
        text: Union[str, None] = None,
        source: Union[Node, None] = None,
        target: Union[Node, None] = None,
    ):
        self.identifier = None
        self.edge_type = edge_type
        self.text = text
        self.source = source
        self.target = target

    def valid(self) -> bool:
        return isinstance(self.source, Node) and isinstance(self.target, Node)

    def to_code(self, file: TextIOBase, indent_level=0, indent_base="    "):
        if not self.valid():
            # Open: raise exception?
            return

        indent_level, indent = get_indent(indent_level, 0, indent_base)
        edge_id = f"{self.identifier}@" if self.identifier else ""
        file.writelines(
            [
                indent,
                self.source.identifier,
                " ",
                edge_id,
                self.edge_type.value,
            ]
        )

        if self.text:
            file.writelines(["|", self.text.replace("|", "`"), "|"])

        file.writelines(
            [
                " ",
                self.target.identifier,
                "\n",
            ]
        )

    def refs_id(self, identifier: str):
        return identifier in (self.source.identifier, self.target.identifier)


class Subgraph(Node):
    def __init__(
        self,
        identifier: str,
        text: Union[str, None] = None,
        direction: Union[FlowchartDirection, None] = None,
        nodes: Union[Iterable[Node], None] = None,
    ):
        super().__init__(identifier=identifier, text=text, shape=NodeShape.DEFAULT)
        self.edges = []
        self.direction = direction
        self.nodes_dict: dict[str, Node] = OrderedDict()
        if nodes:
            for node in nodes:
                self.add(node)
                # TODO: what if someone updates id in Node?

    def get_by_id(self, identifier: str) -> Union[Node, None]:
        found = self.nodes_dict.get(identifier, None)
        if found:
            return found

        # search subgraphs
        for value in self.nodes_dict.values():
            if not isinstance(value, Subgraph):
                continue

            found = value.get_by_id(identifier)
            if found:
                return found

        return None

    def add(self, node: Node):
        self.nodes_dict[node.identifier] = node
        return self

    def remove(self, node: Node):
        found = self.nodes_dict.pop(node.identifier, None)
        if not found:
            for value in self.nodes_dict.values():
                if not isinstance(value, Subgraph):
                    continue
                found = value.remove(node)
                if found:
                    break

        self.edges[:] = [e for e in self.edges if not e.refs_id(node.identifier)]

        return self

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        indent_level, indent = get_indent(indent_level, 0, indent_base)
        e_open, e_close = NodeShape.get_edges(self.shape)

        if self.shape == NodeShape.DEFAULT and not self.text:
            file.writelines([indent, "subgraph ", self.identifier, "\n"])
        else:
            text = self.text if self.text else self.identifier
            file.writelines(
                [
                    indent,
                    "subgraph ",
                    self.identifier,
                    e_open,
                    '"',
                    text,
                    '"',
                    e_close,
                    "\n",
                ]
            )

        if self.direction:
            _, indent_dir = get_indent(indent_level, 1, indent_base)
            file.writelines([indent_dir, "direction ", self.direction.value, "\n"])

        for node in self.nodes_dict.values():
            node.to_code(
                file=file, indent_level=indent_level + 1, indent_base=indent_base
            )

        file.writelines([indent, "end", "\n"])


class SyrenkaFlowchart(Subgraph):
    def __init__(
        self,
        title: str,
        direction: FlowchartDirection,
        nodes: Union[Iterable[Node], None] = None,
    ):
        super().__init__(identifier=title, direction=direction, nodes=nodes)

    def connect(
        self,
        source: Node,
        target: Node,
        edge_type: EdgeType = EdgeType.ARROW_EDGE,
        text: Union[str, None] = None,
    ):
        self.edges.append(Edge(edge_type, text, source=source, target=target))
        # for method-chaining
        return self

    def connect_by_id(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType = EdgeType.ARROW_EDGE,
        text: Union[str, None] = None,
    ):
        source = self.get_by_id(source_id)
        target = self.get_by_id(target_id)

        if source is None or target is None:
            raise ValueError(
                f"one node not found - {source_id=} is {source}, {target_id=} is {target}"
            )

        return self.connect(source, target, edge_type, text)

    def to_code(
        self, file: TextIOBase, indent_level: int = 0, indent_base: str = "    "
    ):
        indent_level, indent = get_indent(indent_level, 0, indent_base)

        if self.identifier:
            file.writelines(get_title(self.identifier))

        if self.direction:
            file.writelines([indent, "flowchart ", self.direction.value, "\n"])
        else:
            file.writelines([indent, "flowchart\n"])

        # easiest workaround for edges going BEHIND subgraphs
        # if i place edges AFTER subgraphs, some might get rendered under subgraph..
        for edge in self.edges:
            edge.to_code(
                file=file, indent_level=indent_level + 1, indent_base=indent_base
            )

        for node in self.nodes_dict.values():
            node.to_code(
                file=file, indent_level=indent_level + 1, indent_base=indent_base
            )

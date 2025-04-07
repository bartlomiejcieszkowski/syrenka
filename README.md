# syrenka
syrenka is mermaid markdown generator

## Description

The aim of this project is to provide easy to use classes for generating mermaid charts and diagrams.

## Installation

`pip install syrenka`

## Example

Diagrams displayed here are generated from mermaid markdown generated by syrenka converted with `mmdc` into svg.

### SyrenkaFlowchart

Here is the simple flowchart:

<!-- EX2_MERMAID_DIAGRAM_BEGIN -->
![SyrenkaFlowchart](https://raw.githubusercontent.com/bartlomiejcieszkowski/syrenka/refs/heads/main/syrenka_diagram-2.svg "SyrenkaFlowchart")
<!-- EX2_MERMAID_DIAGRAM_END -->

and the code behind it:

<!-- EX2_SYRENKA_CODE_BEGIN -->
```python
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
```
<!-- EX2_SYRENKA_CODE_END -->

### SyrenkaClassDiagram
This example uses `importlib.import_module` + `ast` approach.
Here are current classes in syrenka module - syrenka generated mermaid diagram, rendered to svg with use of mmdc:

<!-- EX1_MERMAID_DIAGRAM_BEGIN -->
![SyrenkaClassDiagram](https://raw.githubusercontent.com/bartlomiejcieszkowski/syrenka/refs/heads/main/syrenka_diagram-1.svg "SyrenkaClassDiagram")
<!-- EX1_MERMAID_DIAGRAM_END -->

So how do we get it?
This is a code snippet that does it:

<!-- EX1_SYRENKA_CODE_BEGIN -->
```python
from syrenka.classdiagram import SyrenkaClassDiagram, SyrenkaClassDiagramConfig
from syrenka.base import ThemeNames
from syrenka.lang.python import PythonModuleAnalysis

# from io import StringIO
import sys

class_diagram = SyrenkaClassDiagram(
    "syrenka class diagram", SyrenkaClassDiagramConfig().theme(ThemeNames.neutral)
)
class_diagram.add_classes(
    PythonModuleAnalysis.classes_in_module(module_name="syrenka", nested=True)
)

# file can be anything that implements TextIOBase
# out = StringIO() # string buffer in memory
out = sys.stdout  # stdout
# out = open("syrenka.md", "w") # write it to file

class_diagram.to_code(file=out)

# StringIO
# out.seek(0)
# print(out.read())
```
<!-- EX1_SYRENKA_CODE_END -->

### SyrenkaAstClassDiagram
This is example is using python `ast` approach for generating the class diagram.

<!-- EX3_MERMAID_DIAGRAM_BEGIN -->
![SyrenkaAstClassDiagram](https://raw.githubusercontent.com/bartlomiejcieszkowski/syrenka/refs/heads/main/syrenka_diagram-3.svg "SyrenkaAstClassDiagram")
<!-- EX3_MERMAID_DIAGRAM_END -->

And the code snippet used to generate it:

<!-- EX3_SYRENKA_CODE_BEGIN -->
```python
from syrenka.classdiagram import SyrenkaClassDiagram, SyrenkaClassDiagramConfig
from syrenka.base import ThemeNames
from syrenka.lang.python import PythonModuleAnalysis

from pathlib import Path

# from io import StringIO
import sys

class_diagram = SyrenkaClassDiagram(
    "syrenka class diagram", SyrenkaClassDiagramConfig().theme(ThemeNames.neutral)
)
class_diagram.add_classes(
    PythonModuleAnalysis.classes_in_path(
        Path(__file__).parent.parent / "src"
    )  # , recursive==True)
)

# file can be anything that implements TextIOBase
# out = StringIO() # string buffer in memory
out = sys.stdout  # stdout
# out = open("syrenka.md", "w") # write it to file

class_diagram.to_code(file=out)

# StringIO
# out.seek(0)
# print(out.read())
```
<!-- EX3_SYRENKA_CODE_END -->

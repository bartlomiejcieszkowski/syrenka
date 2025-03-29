from pathlib import Path
from replace_between_tags import replace
import subprocess
import sys

outfile = Path("mermaid.md")
example_path = Path("examples/class_list_module.py")
readme = Path("README.md")

result = subprocess.run(
    ["uv", "run", "python", str(example_path)], encoding="utf-8", capture_output=True
)

print(result.stdout)

with outfile.open("w") as o:
    o.write("```python\n")
    with example_path.open("r") as e:
        o.writelines(e.readlines())

    o.write("```\n")

replace(
    readme, "<!-- EX1_SYRENKA_CODE_BEGIN -->", "<!-- EX1_SYRENKA_CODE_END -->", outfile
)

with outfile.open("w") as o:
    o.write("```cmd\n")

    o.write(result.stdout)
    # to do run
    o.write("```\n")

replace(
    readme,
    "<!-- EX1_MERMAID_DIAGRAM_RAW_BEGIN -->",
    "<!-- EX1_MERMAID_DIAGRAM_RAW_END -->",
    outfile,
)

with outfile.open("w") as o:
    o.write("```mermaid\n")

    o.write(result.stdout)

    o.write("```\n")

replace(
    readme,
    "<!-- EX1_MERMAID_DIAGRAM_BEGIN -->",
    "<!-- EX1_MERMAID_DIAGRAM_END -->",
    outfile,
)

if sys.platform == "win32":
    mmdc_name = "mmdc.cmd"
else:
    mmdc_name = "mmdc"
subprocess.run([mmdc_name, "-i", str(outfile), "-o", "syrenka_diagram.svg"])
outfile.unlink(missing_ok=True)

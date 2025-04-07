from pathlib import Path
from replace_between_tags import replace
import subprocess
import sys


outfile = Path("syrenka_diagram.md")
temp_file = Path("mermaid.tmp")
example_path = Path("examples/class_list_module.py")
example2_path = Path("examples/simple_flowchart.py")
readme = Path("README.md")

examples = [
    {
        "example_path": Path("examples/class_list_module.py"),
        "temp_file": temp_file,
        "target_path": readme,
        "replace_entries": [
            {
                "source": "code",
                "begin": "<!-- EX1_SYRENKA_CODE_BEGIN -->",
                "end": "<!-- EX1_SYRENKA_CODE_END -->",
                "before": "```python\n",
                "after": "```\n",
            },
            {
                "source": "run",
                "begin": "<!-- EX1_MERMAID_DIAGRAM_BEGIN -->",
                "end": "<!-- EX1_MERMAID_DIAGRAM_END -->",
                "before": "```mermaid\n",
                "after": "```\n",
            },
        ],
    },
    {
        "example_path": Path("examples/simple_flowchart.py"),
        "temp_file": temp_file,
        "target_path": readme,
        "replace_entries": [
            {
                "source": "code",
                "begin": "<!-- EX2_SYRENKA_CODE_BEGIN -->",
                "end": "<!-- EX2_SYRENKA_CODE_END -->",
                "before": "```python\n",
                "after": "```\n",
            },
            {
                "source": "run",
                "begin": "<!-- EX2_MERMAID_DIAGRAM_BEGIN -->",
                "end": "<!-- EX2_MERMAID_DIAGRAM_END -->",
                "before": "```mermaid\n",
                "after": "```\n",
            },
        ],
    },
    {
        "example_path": Path("examples/python_classdiagram_from_ast.py"),
        "temp_file": temp_file,
        "target_path": readme,
        "replace_entries": [
            {
                "source": "code",
                "begin": "<!-- EX3_SYRENKA_CODE_BEGIN -->",
                "end": "<!-- EX3_SYRENKA_CODE_END -->",
                "before": "```python\n",
                "after": "```\n",
            },
            {
                "source": "run",
                "begin": "<!-- EX3_MERMAID_DIAGRAM_BEGIN -->",
                "end": "<!-- EX3_MERMAID_DIAGRAM_END -->",
                "before": "```mermaid\n",
                "after": "```\n",
            },
        ],
    },
]


def generate_and_replace(
    example_path: Path, temp_file: Path, target_path: Path, replace_entries: list
):
    result = subprocess.run(
        ["uv", "run", "python", str(example_path)],
        encoding="utf-8",
        capture_output=True,
    )

    for replace_entry in replace_entries:
        replace_in_file(
            target_path=target_path,
            example_path=example_path,
            temp_file=temp_file,
            text=result.stdout,
            **replace_entry,
        )

    return result.stdout


def replace_in_file(
    target_path: Path,
    example_path: Path,
    temp_file: Path,
    text: str,
    source: str,
    begin: str,
    end: str,
    before: str,
    after: str,
):
    if source == "run":
        with temp_file.open("w") as t:
            t.write(before)
            t.write(text)
            t.write(after)
    elif source == "code":
        with temp_file.open("w") as t:
            t.write(before)
            with example_path.open("r") as e:
                t.writelines(e.readlines())

            t.write(after)

    replace(target_path, begin, end, temp_file)


with outfile.open("w") as o:
    for example in examples:
        print(f"# {str(example['example_path'])}")
        o.write("```mermaid\n")
        out = generate_and_replace(**example)
        o.write(out)
        o.write("```\n")

temp_file.unlink(missing_ok=True)

if sys.platform == "win32":
    mmdc_name = "mmdc.cmd"
else:
    mmdc_name = "mmdc"
subprocess.run([mmdc_name, "-i", str(outfile), "-o", "syrenka_diagram.svg"])

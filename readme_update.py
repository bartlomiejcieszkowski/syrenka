"""Script for updating README.md"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from replace_between_tags import replace
from syrenka.generate import generate_diagram_image

OUT_FILE = Path("syrenka_diagram.md")
TEMP_FILE = Path("mermaid.tmp")
README = Path("README.md")

examples = [
    {
        "example_path": Path("examples/class_list_module.py"),
        "temp_file": TEMP_FILE,
        "target_path": README,
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
        "temp_file": TEMP_FILE,
        "target_path": README,
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
        "temp_file": TEMP_FILE,
        "target_path": README,
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
    """Runs code and replaces text in given file with its output."""
    result = subprocess.run(
        ["uv", "run", "python", str(example_path)],
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    for replace_entry in replace_entries:
        replacement = Replacement(text=result.stdout, **replace_entry)
        replace_in_file(
            target_path=target_path,
            example_path=example_path,
            temp_file=temp_file,
            replacement=replacement,
        )

    return result.stdout


@dataclass
class Replacement:
    """Dataclass for replacement"""

    text: str
    source: str
    begin: str
    end: str
    before: str
    after: str


def replace_in_file(
    target_path: Path, example_path: Path, temp_file: Path, replacement: Replacement
):
    """replaces text between markers in given file"""
    if replacement.source == "run":
        with temp_file.open("w") as t:
            t.write(replacement.before)
            t.write(replacement.text)
            t.write(replacement.after)
    elif replacement.source == "code":
        with temp_file.open("w", encoding="utf-8") as t:
            t.write(replacement.before)
            with example_path.open("r") as e:
                t.writelines(e.readlines())

            t.write(replacement.after)

    replace(target_path, replacement.begin, replacement.end, temp_file)


with OUT_FILE.open("w", encoding="utf-8") as o:
    for example in examples:
        print(f"# {str(example['example_path'])}")
        o.write("```mermaid\n")
        out = generate_and_replace(**example)
        o.write(out)
        o.write("```\n")

TEMP_FILE.unlink(missing_ok=True)

generate_diagram_image(OUT_FILE, Path("syrenka_diagram.svg"), overwrite=True)

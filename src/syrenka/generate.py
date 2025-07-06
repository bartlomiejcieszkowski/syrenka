import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union

MMDC_DEFAULT = "mmdc"
MMDC_EXE = os.environ.get("SYRENKA_MMDC", MMDC_DEFAULT)
MMDC_SUPPORT = False

p = shutil.which(MMDC_EXE)
if p:
    MMDC_EXE = str(Path(p).resolve())
    MMDC_SUPPORT = True

if not MMDC_SUPPORT:
    print(
        "For local mermaid diagram generation there needs to be mermaid-cli installed\n"
        f"For different executable name set SYRENKA_MMDC env variable, default is '{MMDC_DEFAULT}'"
        "see https://github.com/mermaid-js/mermaid-cli for reference",
        file=sys.stderr,
    )


def generate_diagram_image(
    input: Union[str, Path], output_file: Path, overwrite: bool = False
):
    if not MMDC_SUPPORT:
        print(
            "For mermaid diagram generation install mmdc, check stderr", file=sys.stderr
        )
        return

    of = output_file.resolve()
    if of.exists() and not overwrite:
        raise FileExistsError(
            f"Output file: {of}, already exists and overwrite is {overwrite}"
        )

    if isinstance(input, Path):
        input_str = None
        input_arg = str(input)
    elif isinstance(input, str):
        input_str = input
        input_arg = "-"
    else:
        raise ValueError(f"unexpected input type: {type(input)} - expected Path or str")

    args = [MMDC_EXE, "-i", input_arg, "-o", str(of)]
    subprocess.run(args, input=input_str, text=True, capture_output=True, check=False)

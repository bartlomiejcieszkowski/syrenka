import subprocess
import sys

from pathlib import Path

import os
import shutil

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

    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool = False):
        print(
            "For mermaid diagram generation install mmdc, check stderr", file=sys.stderr
        )
else:

    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool = False):
        of = output_file.resolve()
        if of.exists() and not overwrite:
            raise Exception()

        mcode = "\n".join(mcode_lines)
        subprocess.run(
            [MMDC_EXE, "-i", "-"], input=mcode, text=True, capture_output=True
        )

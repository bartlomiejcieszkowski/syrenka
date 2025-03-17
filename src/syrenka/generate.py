import subprocess
import sys

from pathlib import Path

import os

MMDC_PATH_DEFAULT = "mmdc.cmd" if sys.platform == "win32" else "mmdc"

MMDC_PATH = os.environ.get("SYRENKA_MMDC", MMDC_PATH_DEFAULT)
MMDC_SUPPORT = False
try:
    if subprocess.run([MMDC_PATH, "--help"], check=True, capture_output=True):
        MMDC_SUPPORT = True
except Exception:
    pass

if not MMDC_SUPPORT:
    print(
        "For local mermaid diagram generation there needs to be mermaid-cli installed\n"
        "see https://github.com/mermaid-js/mermaid-cli for reference",
        file=sys.stderr,
    )

    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool = False):
        raise Exception()
else:

    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool = False):
        of = output_file.resolve()
        if of.exists() and not overwrite:
            raise Exception()

        mcode = "\n".join(mcode_lines)
        subprocess.run(
            [MMDC_PATH, "-i", "-"], input=mcode, text=True, capture_output=True
        )

import subprocess
import sys

from pathlib import Path

mmdc_support = False
try:
    if subprocess.run("mmdc.cmd --help", check=True, capture_output=True):
        mmdc_support = True
except Exception:
    pass

if not mmdc_support:
    print("For local mermaid diagram generation there needs to be mermaid-cli installed", file=sys.stderr)
    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool=False):
        raise Exception()
else:
    
    def generate_from_lines(mcode_lines, output_file: Path, overwrite: bool=False):
        of = output_file.resolve()
        if of.exists() and not overwrite:
            raise Exception()


        mcode = '\n'.join(mcode_lines)
        subprocess.run("mmdc.cmd -i -", input=mcode, text=True, capture_output=True)

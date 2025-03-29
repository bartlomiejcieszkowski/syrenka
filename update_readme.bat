echo ```python> mermaid_diagram.md
type examples\class_list_module.py >> mermaid_diagram.md
echo. >> mermaid_diagram.md
echo ```>> mermaid_diagram.md

python replace_between_tags.py -s "<!-- EX1_SYRENKA_CODE_BEGIN -->" -e "<!-- EX1_SYRENKA_CODE_END -->" -f README.md -r mermaid_diagram.md

echo ```cmd> mermaid_diagram.md
uv run python examples\class_list_module.py >> mermaid_diagram.md
echo ```>> mermaid_diagram.md
python replace_between_tags.py -s "<!-- EX1_MERMAID_DIAGRAM_RAW_BEGIN -->" -e "<!-- EX1_MERMAID_DIAGRAM_RAW_END -->" -f README.md -r mermaid_diagram.md

echo ```mermaid> mermaid_diagram.md
uv run python examples\class_list_module.py >> mermaid_diagram.md
echo ```>> mermaid_diagram.md
python replace_between_tags.py -s "<!-- EX1_MERMAID_DIAGRAM_BEGIN -->" -e "<!-- EX1_MERMAID_DIAGRAM_END -->" -f README.md -r mermaid_diagram.md

mmdc -i mermaid_diagram.md -o mermaid_diagram.svg

del mermaid_diagram.md

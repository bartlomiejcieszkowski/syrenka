echo ```mermaid> mermaid_diagram.txt
uv run python examples\class_list_module.py >> mermaid_diagram.txt
echo ```>> mermaid_diagram.txt
python replace_between_tags.py -s "<!-- EX1_MERMAID_DIAGRAM_BEGIN -->" -e "<!-- EX1_MERMAID_DIAGRAM_END -->" -f README.md -r mermaid_diagram.txt

echo ```python> mermaid_diagram.txt
type examples\class_list_module.py >> mermaid_diagram.txt
echo. >> mermaid_diagram.txt
echo ```>> mermaid_diagram.txt

python replace_between_tags.py -s "<!-- EX1_SYRENKA_CODE_BEGIN -->" -e "<!-- EX1_SYRENKA_CODE_END -->" -f README.md -r mermaid_diagram.txt

echo ```cmd> mermaid_diagram.txt
uv run python examples\class_list_module.py >> mermaid_diagram.txt
echo ```>> mermaid_diagram.txt
python replace_between_tags.py -s "<!-- EX1_MERMAID_DIAGRAM_RAW_BEGIN -->" -e "<!-- EX1_MERMAID_DIAGRAM_RAW_END -->" -f README.md -r mermaid_diagram.txt

del mermaid_diagram.txt
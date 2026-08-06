"""Read-only .ipynb inspection helper — avoids loading full notebook JSON (incl. embedded
images) through the Read tool, which blows past token limits on notebooks with plotted output.

Usage:
    python3 tools/inspect_notebook.py list-cells <notebook.ipynb>
    python3 tools/inspect_notebook.py cell <notebook.ipynb> --id <cell_id>
    python3 tools/inspect_notebook.py cell <notebook.ipynb> --index <n>
    python3 tools/inspect_notebook.py find-images <notebook.ipynb>
    python3 tools/inspect_notebook.py search <notebook.ipynb> <substring>
"""

import argparse
import json


def load(path):
    with open(path) as f:
        return json.load(f)


def source_text(cell):
    return "".join(cell.get("source", []))


def list_cells(nb, preview_len=80):
    for i, cell in enumerate(nb["cells"]):
        preview = source_text(cell)[:preview_len].replace("\n", " ")
        print(f"[{i}] id={cell.get('id')} type={cell.get('cell_type')}: {preview}")


def show_cell(nb, cell_id=None, index=None):
    for i, cell in enumerate(nb["cells"]):
        if (cell_id is not None and cell.get("id") == cell_id) or (index is not None and i == index):
            print(f"=== cell {i} id={cell.get('id')} type={cell.get('cell_type')} ===")
            print(source_text(cell))
            return
    print("cell not found")


def find_images(nb):
    for i, cell in enumerate(nb["cells"]):
        has_img = any("image" in k for out in cell.get("outputs", []) for k in out.get("data", {}))
        if has_img:
            preview = source_text(cell)[:150].replace("\n", " ")
            print(f"[{i}] id={cell.get('id')}: {preview}")


def search(nb, substring):
    for i, cell in enumerate(nb["cells"]):
        text = source_text(cell)
        if substring in text:
            preview = text[:150].replace("\n", " ")
            print(f"[{i}] id={cell.get('id')}: {preview}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-cells")
    p_list.add_argument("notebook")

    p_cell = sub.add_parser("cell")
    p_cell.add_argument("notebook")
    p_cell.add_argument("--id")
    p_cell.add_argument("--index", type=int)

    p_images = sub.add_parser("find-images")
    p_images.add_argument("notebook")

    p_search = sub.add_parser("search")
    p_search.add_argument("notebook")
    p_search.add_argument("substring")

    args = parser.parse_args()
    nb = load(args.notebook)

    if args.command == "list-cells":
        list_cells(nb)
    elif args.command == "cell":
        show_cell(nb, cell_id=args.id, index=args.index)
    elif args.command == "find-images":
        find_images(nb)
    elif args.command == "search":
        search(nb, args.substring)


if __name__ == "__main__":
    main()

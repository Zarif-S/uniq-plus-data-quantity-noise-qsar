#!/usr/bin/env python3
"""Git clean filter: strip notebook outputs/execution counts before they enter git's object
store. Only affects what git commits -- the working tree file on disk is untouched, so local
Jupyter sessions keep their outputs."""
import sys

import nbformat

nb = nbformat.read(sys.stdin, as_version=4)
for cell in nb.cells:
    if cell.get("cell_type") == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
nbformat.write(nb, sys.stdout)

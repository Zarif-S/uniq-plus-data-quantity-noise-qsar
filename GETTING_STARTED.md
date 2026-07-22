# Getting Started — UNIQ+

Welcome to **UNIQ+** — a 6-week academic research project investigating how dataset size
and label noise affect ML model performance for molecular property prediction (QSAR).

---

## Prerequisites

- Python 3.10
- [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Setup

```bash
git clone <repository-url>
cd UNIQ+
uv sync                      # installs all pinned deps
source .venv/bin/activate    # macOS/Linux
jupyter lab                  # opens in browser
```

No environment variables required — all datasets are open source and local.

---

## Where to go next

| I want to…                          | Read this                          |
|-------------------------------------|------------------------------------|
| Understand the project fully        | [CLAUDE.md](CLAUDE.md)             |
| See what we're working on this week | [PROJECT_PLAN.md](PROJECT_PLAN.md) |
| Understand the research goals       | [ROADMAP.md](ROADMAP.md)           |
| Run the notebooks                   | `notebooks/` — start with `01_adme_eda_baseline.ipynb` |
| Run the tests                       | `uv run pytest tests/`             |

---

**New to the agentic-coding-framework doc structure used here?**
See [`docs/agentic-framework-guide.md`](docs/agentic-framework-guide.md).

---

**Last Updated**: 2026-07-20

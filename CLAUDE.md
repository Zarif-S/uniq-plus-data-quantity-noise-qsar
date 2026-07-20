# Claude Code Configuration - UNIQ+

## Project Overview

**UNIQ+** (Data Quantity, Noise & ML in Drug Discovery QSAR) investigates how dataset size and label noise affect machine learning model performance for molecular property prediction. The project uses two datasets:
- **ADME dataset**: 3521 compounds, 6 endpoints (HLM/RLM clearance, MDR1 efflux, solubility, PPB human/rat)
- **PDE10A dataset**: PDE10A inhibitors with pIC50 values and 7 split strategies (temporal 2011–2013, chemotype-based, random)

### Key Technologies
- Python 3.11 (managed via uv)
- ML: scikit-learn, XGBoost, LightGBM, DeepChem 2.8.0, ChemProp 1.6.1
- Cheminformatics: RDKit 2023.9.5
- Deep learning: PyTorch 2.0.1
- Visualisation: Plotly, Matplotlib

### Current Status
✅ Environment set up and pinned (pyproject.toml + uv.lock)
✅ ADME public dataset loaded (3521 compounds, 6 endpoints)
🔄 Exploratory data analysis
⏳ Baseline ML models (RF, XGBoost, LightGBM)
⏳ Data quantity experiments (learning curves)
⏳ Label noise experiments
⏳ Deep learning models (ChemProp, DeepChem)

---

## Documentation Navigation

**What are you trying to do?**

```
┌────────────────────────────────────────────────────────────────┐
│ TASK                              → READ THIS FIRST            │
├────────────────────────────────────────────────────────────────┤
│ Setup project & install deps     → This file (below)          │
│ Understand strategic vision      → ROADMAP.md                 │
│ See current sprint/iteration     → PROJECT_PLAN.md            │
│ Review recent changes            → CHANGELOG.md               │
│ Cross-concept event flows        → SYNCHRONIZATIONS.md        │
├────────────────────────────────────────────────────────────────┤
│ src/ modules (EDA, Features, Plotting) → src/CLAUDE.md        │
│ Cleaning module (NaN filter, IQR)      → src/cleaning/CLAUDE.md│
│ Models module (baselines, evaluation)  → src/models/CLAUDE.md  │
│ Splitting module (PDE10A 7 strategies) → src/splitting/CLAUDE.md│
│ Tuning module (LightGBM, MPNN2)        → src/tuning/CLAUDE.md   │
├────────────────────────────────────────────────────────────────┤
│ All logged decisions (ADR)       → DECISIONS.md               │
│ Process & technical lessons      → LESSONS_LEARNED.md         │
└────────────────────────────────────────────────────────────────┘
```

**For AI agents**: Read this file first, then follow the navigation table above to find module-specific context. Check [PROJECT_PLAN.md](PROJECT_PLAN.md) for current priorities before implementing features.

---

## Environment Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install (pinned environment)
git clone [repository-url]
cd UNIQ+
uv sync   # installs all pinned deps from uv.lock

# Activate the virtual environment
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Launch a notebook
jupyter lab
```

No environment variables required — all data is open source and loaded from local files.

---

## Project Structure

```
UNIQ+/
├── notebooks/                # Jupyter notebooks — EDA, experiments, results
│   ├── 01_eda_adme.ipynb
│   ├── 02_eda_pde10a.ipynb
│   └── ...
├── src/                      # Reusable Python modules imported by notebooks
│   ├── features.py           # Fingerprint/descriptor computation (RDKit)
│   ├── plotting.py           # Reusable plot functions (Matplotlib/Plotly)
│   ├── models.py             # Model wrappers and training utilities
│   └── noise.py              # Label noise injection utilities (future)
├── data/
│   ├── raw/                  # Original datasets, never modified
│   └── processed/            # Cleaned/featurised data
├── tests/                    # Sanity tests for src/ modules
├── pyproject.toml            # Dependencies (managed via uv)
├── uv.lock                   # Pinned lockfile
├── CLAUDE.md                 # This file
├── ROADMAP.md
├── PROJECT_PLAN.md
├── CHANGELOG.md
├── DECISIONS.md              # Architectural decision records (ADR)
└── LESSONS_LEARNED.md        # Post-project lessons
```

---

## Common Tasks

### Running notebooks

```bash
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
jupyter lab       # opens in browser
```

### Running tests

```bash
uv run pytest tests/
```

### Adding a new dependency

```bash
uv add <package>   # updates pyproject.toml and uv.lock
```

### Notebook workflow

1. Notebooks go in `notebooks/`, named with a number prefix (`01_`, `02_`, …)
2. Every notebook must run top-to-bottom from a fresh kernel — verify before committing
3. If a helper function is used in more than one notebook, move it to `src/`

---

## Coding Conventions

This is a 6-week academic research project. Conventions are minimal but non-negotiable.

### What we do
- **Notebooks runnable top-to-bottom**: always verify with Kernel → Restart & Run All before treating results as final
- **Extract to `src/` when**: a function is called in more than one notebook, or is longer than ~20 lines
- **`src/` functions get a one-line docstring** and a corresponding sanity test in `tests/`
- **Run `ruff check src/ tests/`** occasionally (not on every save) to catch obvious issues

### What we skip
- Type hints, full docstrings, CI, PRs, code reviews — not warranted for this scope
- No `ruff format` enforced in notebooks (too disruptive to exploratory flow)

### RDKit is the first resort
RDKit handles most cheminformatics natively. Before writing custom code for fingerprints, descriptors, similarity, or 2D/3D operations, check RDKit docs first (context7 ID: `/websites/rdkit`). Custom helpers in `src/` should be thin wrappers around RDKit + plotting, not reimplementations.

---

## Known Issues & Solutions

<!-- Add entries as they arise: -->
<!-- **[✅ RESOLVED | 🔄 IN PROGRESS | ⚠️ KNOWN LIMITATION]: [Title]** -->
<!-- - **Issue**: [Description] -->
<!-- - **Solution/Workaround**: [How it's handled] -->

---

---

## Agent Working Agreements

> TODO: Once finalised here, migrate this section into the `agentic-coding-framework` CLAUDE.md template so all projects inherit it.

### Think before coding
- State assumptions explicitly; if uncertain, ask. Present multiple interpretations — don't pick silently.
- Before using a specific scientific library, fetch its current docs via context7 on demand — one library at a time, only when actively working with it. Do not fetch speculatively.
  - RDKit → context7 library ID: `/websites/rdkit` (30,668 snippets, high reputation)
  - Other libraries (DeepChem, ChemProp, etc.) → resolve and add here as needed

### Goal-driven execution
For multi-step work, open with a brief plan:
```
1. [step] → verify: [check]
2. [step] → verify: [check]
```

### Grounding
Label every result `verified` (ran it, output shown) or `expected` (reasoned, not run). Never report a result not observed in tool output.

### Subagents
Delegate independent subtasks and keep working while they run. Intervene if one drifts or lacks context.

### Final summary
Your closing message is for someone who saw none of your working steps. Lead with the outcome in one sentence, then supporting detail, then what you need from them. Complete sentences, no shorthand.

---

**Last Updated**: 2026-07-13 | **Status**: Active development | **Maintainers**: Zarif

**Docs**: [ROADMAP.md](ROADMAP.md) · [PROJECT_PLAN.md](PROJECT_PLAN.md) · [DECISIONS.md](DECISIONS.md) · [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

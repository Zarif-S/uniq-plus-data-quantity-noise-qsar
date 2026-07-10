# UNIQ+ — OPIG, Data Quantity, Noise & ML in Drug Discovery, QSAR

Project investigates how dataset size and label noise affect machine learning model performance for molecular property prediction (QSAR). It is a 6-week academic research project using two real-world drug discovery datasets and a range of ML approaches from classical fingerprint-based models to deep learning.

---

## Research Questions

1. How does training set size affect predictive performance across ADME endpoints?
2. How much label noise can ML models tolerate before performance degrades significantly?
3. Do deep learning models (ChemProp, DeepChem) show different noise sensitivity than classical models (RF, XGBoost)?

---

## Datasets

| Dataset | Compounds | Endpoints | Source |
|---------|-----------|-----------|--------|
| ADME public set | 3,521 | HLM/RLM clearance, MDR1 efflux, solubility, PPB (human/rat) | Public |
| PDE10A inhibitors | ~TBD | pIC50 | Public |

The PDE10A dataset includes 7 split strategies: temporal (2011–2013), chemotype-based, and random — enabling evaluation of model generalisation under realistic deployment conditions.

---

## Setup

Requires Python 3.10 and [uv](https://github.com/astral-sh/uv).

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install pinned environment
git clone <repository-url>
cd UNIQ+
uv sync

# Activate and launch
source .venv/bin/activate
jupyter lab
```

No environment variables required — all datasets are open source and loaded from local files.

---

## Project Structure

```
UNIQ+/
├── notebooks/          # EDA, experiments, results (numbered: 01_, 02_, ...)
├── src/                # Reusable modules imported by notebooks
│   ├── features.py     # Fingerprint/descriptor computation (RDKit)
│   ├── models.py       # Model wrappers and training utilities
│   ├── plotting.py     # Reusable plot functions
│   └── noise.py        # Label noise injection (upcoming)
├── data/
│   ├── raw/            # Original datasets, never modified
│   └── processed/      # Cleaned/featurised data
├── tests/              # Sanity tests for src/ modules
└── pyproject.toml      # Dependencies (managed via uv)
```

---

## Current Status

| Phase | Status |
|-------|--------|
| Environment setup | Done |
| ADME dataset loaded | Done |
| Exploratory data analysis | In progress |
| Baseline ML models (RF, XGBoost, LightGBM) | Upcoming |
| Data quantity experiments (learning curves) | Upcoming |
| Label noise experiments | Upcoming |
| Deep learning (ChemProp, DeepChem) | Upcoming |

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the current sprint and [ROADMAP.md](ROADMAP.md) for the full research timeline.

---

## Running Tests

```bash
uv run pytest tests/
```

---

## Documentation

- [ROADMAP.md](ROADMAP.md) — Research timeline and milestones
- [PROJECT_PLAN.md](PROJECT_PLAN.md) — Current sprint
- [DECISIONS.md](DECISIONS.md) — Architectural decision records
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) — Post-project lessons
- [CHANGELOG.md](CHANGELOG.md) — Change history

---

## Built With

This project uses the [Strategic Agentic Coding Framework](https://github.com/Zarif-S/agentic-coding-framework) for documentation structure and AI-agent workflow — a hierarchical doc system (CLAUDE.md / ROADMAP.md / PROJECT_PLAN.md) that keeps AI coding assistants context-efficient across a project. See [`docs/agentic-framework-guide.md`](docs/agentic-framework-guide.md) for a local quickstart guide.

---

**Last Updated**: 2026-07-10 | **Status**: Active development | **Maintainer**: Zarif

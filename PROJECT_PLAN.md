# Project Plan - Tactical Execution

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Looking for strategic vision?** → [ROADMAP.md](ROADMAP.md)
- **Looking for pipeline handoffs?** → [SYNCHRONIZATIONS.md](SYNCHRONIZATIONS.md)
- **Looking for completed features?** → [CHANGELOG.md](CHANGELOG.md)

---

## Purpose of This Document

**For AI Agents**: Understand current priorities and context before implementing features. Use TodoWrite for task-level breakdown within a session.

**For Humans**: High-level status overview bridging ROADMAP strategy to execution.

**PROJECT_PLAN.md** focuses on **what** and **when**:
- **What** are we building/doing right now?
- **When** is this happening? (now / next / later)

This is NOT task-level tracking or strategic vision — see ROADMAP.md for strategy.

**Timeframe**: Current focus + next 1-2 weeks, reviewed at end of each phase.

---

## Current Focus (Week 1–2, July 2026)

**Theme**: EDA + Baseline Models — ADME dataset

**Strategic Alignment**: ROADMAP Phase 1 — *"Understand the ADME dataset and establish a working baseline pipeline"*

---

## What We're Building

### Now (In Progress)

**1. Exploratory Data Analysis (ADME)**
- **What**: Distribution plots for all 6 endpoints, SMILES validity check, missing value report, endpoint correlation matrix, summary statistics
- **Why**: Required before any cleaning or modelling decisions; gates SYNC-002 (cleaning strategy) and SYNC-003 (split strategy)
- **Status**: Not yet started
- **Next milestone**: Complete `notebooks/01_eda_adme.ipynb`; decide cleaning strategy (SYNC-002 outcome)

### Next (Coming Soon)

**1. Data Cleaning (ADME)**
- **What**: Handle missing values, remove invalid SMILES, standardize structures
- **Why**: Clean data is required before featurization and model training
- **Depends on**: EDA outcomes (SYNC-002 TBD — strategy not yet decided)

**2. Train/Test Splitting (ADME)**
- **What**: Define train/test split strategy for ADME
- **Why**: Must be fixed before baseline model evaluation to avoid data leakage
- **Depends on**: EDA complete (SYNC-003 TBD — strategy not yet decided)
- **Decision needed**: Random split confirmed for Phase 1 baseline; revisit in Phase 3 for PDE10A

**3. Featurization (ADME)**
- **What**: Convert SMILES to ML-ready features
- **Why**: Required input for all ML models
- **Depends on**: EDA complete
- **Decision**: ECFP4 confirmed primary; `src/features.py` implements both Morgan fingerprints and RDKit 2D descriptors; swap is trivial

**4. Baseline Models (ADME)**
- **What**: Train Linear Regression, Random Forest, XGBoost, LightGBM on all 6 ADME endpoints; evaluate with R², RMSE, MSE; predicted-vs-actual plots
- **Why**: Exit criterion for Phase 1; gates Phase 2 learning curve experiments
- **Depends on**: Featurization complete

### Later (On Deck)

- **Phase 2** (Week 3): Learning curves / data quantity experiments on ADME
- **Phase 3** (Week 4): PDE10A EDA + baseline models + 7-way split strategy comparison
- **Phase 4** (Weeks 5–6): Label noise injection + robustness analysis + writeup
- **TBD**: Deep learning models (ChemProp, DeepChem, Tx-Gemma) — review after Phase 2 based on time remaining

---

## Active Decisions Pending

**Deep learning models**
- **Blocks**: Nothing yet — Phase 4 consideration
- **Owner**: Zarif to investigate Tx-Gemma dataset size suitability
- **ETA**: End of Phase 2 (Week 3)

---

## Recently Completed

**✅ Environment Setup**
- **Completed**: Week 1 (early July 2026)
- **Outcome**: Python 3.10 env pinned via uv (pyproject.toml + uv.lock); all deps installable with `uv sync`

**✅ Project Scaffolding**
- **Completed**: Week 1 (early July 2026)
- **Outcome**: Folder structure created (src/, notebooks/, tests/, data/raw/, data/processed/)

**✅ Data Acquisition**
- **Completed**: Week 1 (early July 2026)
- **Outcome**: ADME dataset (3521 compounds, 6 endpoints) and PDE10A dataset in data/raw/

**✅ Documentation Foundation**
- **Completed**: Week 1 (early July 2026)
- **Outcome**: CLAUDE.md, ROADMAP.md, SYNCHRONIZATIONS.md, LESSONS_LEARNED.md all populated

---

## Key Links

**Related Documentation**:
- [ROADMAP.md](ROADMAP.md) — Strategic vision and phased plan
- [SYNCHRONIZATIONS.md](SYNCHRONIZATIONS.md) — Cross-step decision handoffs (SYNC-001 through SYNC-009)
- [CLAUDE.md](CLAUDE.md) — Environment setup and coding conventions
- [CHANGELOG.md](CHANGELOG.md) — Feature history

---

## For AI Agents

When asked to implement something:

1. **Read this document** to understand current focus
2. **Check "Active Decisions Pending"** — do not implement featurization or splitting without those being resolved
3. **Check SYNCHRONIZATIONS.md** for relevant SYNC gates before starting work that depends on prior decisions
4. **Use TodoWrite** for task-level breakdown within your session
5. **Update this document and CHANGELOG.md** when an initiative completes

Task lists are ephemeral (conversation-level). This document stays high-level.

---

**Last Updated**: 2026-07-10
**Review Cadence**: End of each phase (every 1–2 weeks)
**Current Period**: Week 1–2, Phase 1

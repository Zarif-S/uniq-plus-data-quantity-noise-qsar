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

**Phase 2 — PDE10A EDA + Baseline Models**
- **What**: EDA on PDE10A dataset; baseline models across all 7 split strategies (temporal 2011–2013, chemotype-based, random); split strategy comparison
- **Why**: Completing both dataset baselines before designing experiments gives supervisors a full picture; split strategy decisions (which to use for learning curves, noise injection) are better made with PDE10A baselines in hand
- **Status**: Not yet started
- **Next milestone**: `notebooks/02_eda_baseline_pde10a.ipynb`

### Recently Completed (Phase 1)

**✅ EDA (ADME)** — `notebooks/01_adme_eda_baseline.ipynb` Sections 1.1–1.10
- SMILES validity (100% valid), duplicate check (0), missing value report, outlier detection (3σ + IQR), distributions, correlations, chemical space (Lipinski Ro5)

**✅ Data Cleaning (ADME)** — Sections 1.11–1.12
- Strategy: per-endpoint NaN filtering (ADR-002); IQR 1.5× outlier flagging (flag-only); effective N table per endpoint

**✅ Featurization (ADME)** — Section 2.1
- ECFP4 Morgan fingerprints (radius=2, 2048 bits) via `src/features.morgan_fingerprints`; per-endpoint filtered subsets

**✅ Train/Test Split** — Section 2.2
- 80/20 random split per endpoint, seed=42

**✅ Baseline Models (ADME)** — Sections 2.3–2.5
- 5 models × 6 endpoints: LinearRegression, BayesianRidge, RandomForest, XGBoost, LightGBM
- Metrics: R², RMSE; results table + predicted vs actual plots

### Later (On Deck)

- **Phase 3** (Weeks 4–6): Learning curves + noise injection — scope and dataset coverage to be agreed with supervisors at Phase 2 review
- **TBD**: Deep learning models (ChemProp, DeepChem) — review after Phase 2 based on time remaining

---

## Active Decisions Pending

**Deep learning models**
- **Blocks**: Nothing yet — Phase 4 consideration
- **Owner**: Zarif to investigate ChemProp/DeepChem/ Tx-Gemma inclusion
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

**Last Updated**: 2026-07-13
**Review Cadence**: End of each phase (every 1–2 weeks)
**Current Period**: Week 2–3, Phase 2

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

## Current Focus (Week 3–4, July 2026)

**Theme**: ADME dataset — Hyperparameter tuning, learning curves, and noise injection

**Strategic Alignment**: ROADMAP Phases 3–6 — *"Tune models, then quantify how data quantity and label noise affect performance"*

---

## What We're Building

### Now (In Progress)

**Phase 3 — Baseline Tuning (Clean Data Reference)**
- **What**: Tune LightGBM, RF, MPNN2 on clean full training data (4 endpoints) to validate tuning pipeline and establish clean-data reference
- **Why**: Need a working tuning pipeline before the experiment loop; clean-data tuned R² serves as the ceiling for comparison
- **Status**: Module ready (`src/tuning/`), notebook cells written — needs execution
- **Module**: `src/tuning/` — see [src/tuning/CLAUDE.md](src/tuning/CLAUDE.md)

### Next (On Deck)

**Phase 4 — Learning Curves (Quantity Axis)**
- Two arms: **baseline** (default hyperparams) vs **tuned** (re-tune at each fraction via RandomizedSearchCV)
- Vary fractions ∈ {0.05, 0.10, 0.25, 0.50, 0.75, 1.0}; 10 seeds per fraction
- Metrics recorded per run: R², RMSE, MAE, Spearman ρ, CCC
- Compare: does tuning help or hurt at small N?

**Phase 5 — Noise Injection (Noise Axis)**
- Two arms: **baseline** vs **tuned** (re-tune on noisy data — CV folds inherit noise)
- Three noise types (Landrum & Riniker): Gaussian (intra-assay), systematic bias (inter-assay), gross errors (annotation)
- Training labels only — test always clean; 10 seeds per level
- Metrics recorded per run: R², RMSE, MAE, Spearman ρ, CCC
- **Gaussian ceiling**: `NoiseEstimator` (ChemRxiv 2024) theoretical R² = 1 − σ²/Var(y) overlaid on Gaussian plots — reference for CV tuner guidance and field-deployment performance (Gaussian only)

**Phase 5b — Validation Set Quality Sub-Experiment**
- At 3 representative sizes (full N, 25%, 5%): compare noisy validation (realistic) vs clean validation (ideal) during tuning
- Answers: how important is a clean validation set for hyperparameter selection under noise?

**Phase 6 — 2D Grid + Writeup**
- All (N, noise_level) combinations for both arms; 5 seeds per cell
- Surface plots, baseline vs tuned comparison, validation quality findings
- Writeup: clean notebooks, figures, results summary

### Parked

**PDE10A — EDA + Baseline Models**
- **Status**: Complete — `notebooks/02_eda_baseline_pde10a.ipynb`
- **Why parked**: Focus shifted to ADME dataset for learning curve and noise experiments. PDE10A baselines are done and can be revisited for cross-dataset comparison after ADME experiments are complete.

---

## Recently Completed

**✅ Phase 2 — PDE10A EDA + Baseline Models** (Week 3)
- EDA, baseline models across 7 split strategies, split strategy comparison
- Key finding: distribution shift dominates on 5/7 splits; MW beats ECFP4 on hard splits

**✅ Phase 1 — ADME EDA + Baseline Models** (Weeks 1–2)
- EDA (SMILES validity, missing values, outliers, distributions, correlations, chemical space, pairwise similarity)
- Data cleaning (per-endpoint NaN filtering, IQR flagging, stereoisomer exclusion)
- Featurization (ECFP4 Morgan fingerprints, radius=2, 2048 bits)
- Train/test split (80/20 random, seed=42)
- 6 models × 6 endpoints with R², RMSE, MAE, Spearman ρ, CCC; predicted vs actual plots; similarity-binned MAE

**✅ Environment Setup & Scaffolding** (Week 1)
- Python 3.11 env pinned via uv; folder structure; ADME + PDE10A datasets acquired; documentation foundation

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

**Last Updated**: 2026-07-20
**Review Cadence**: End of each phase (every 1–2 weeks)
**Current Period**: Week 3–4, Phase 3 (ADME)

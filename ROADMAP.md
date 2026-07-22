# Roadmap - Strategic Vision

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Current work?** → [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Previous roadmap (parked experiments)?** → [OLD_ROADMAP.md](OLD_ROADMAP.md)

---

## Known Discrepancies with the Paper

- **Fingerprint radius**: The Fang et al. (2023) paper text states "radius 4 (FCFP4)" — but these contradict each other. FCFP4 means diameter=4, which is radius=2. Their code (`ADME_ML_public.py` line 187) correctly uses `radius=2, nBits=1024, useFeatures=True`, i.e. FCFP4. The paper text confuses radius with diameter. We follow the code: radius=2, FCFP4.

---

## Current Focus: Reference Paper Recreation

**Goal**: Reproduce the published results from the reference paper (Biogen public ADME dataset) as faithfully as possible before designing original experiments on top.

**Why this first**: Reproducing published results validates our pipeline, confirms data handling is correct, and establishes credible baselines grounded in the literature. Any deviations from published numbers become a documented, explainable finding rather than an unknown bug.

**Paper**: [TO FILL IN — title, authors, DOI]

---

## Phases

### Phase R1 — Paper Recreation (`01.5_adme_biogen_public_recreation.ipynb`)

**Goal**: Match the paper's reported metrics as closely as possible using the same dataset, same endpoints, and (where described) the same models and splits.

**Initiatives**:
1. Read and document the paper's exact methodology — featurization, models, split strategy, metrics reported
2. Replicate each model/split combination in the notebook
3. Record our reproduced numbers alongside the paper's numbers in a comparison table
4. Document any deviations and their likely causes (e.g., random seed, library version, underdefined preprocessing)

**Exit criteria**: Comparison table with paper vs reproduced metrics for all reported models/endpoints. Deviations explained or flagged.

---

### Phase R2 — Original Experiments (Parked)

The learning curve, noise injection, and 2D grid experiments from the original roadmap are parked. See [OLD_ROADMAP.md](OLD_ROADMAP.md) for full design.

**Will resume when**: Paper recreation is complete and validated.

---

## Key Links

[PROJECT_PLAN.md](PROJECT_PLAN.md) · [OLD_ROADMAP.md](OLD_ROADMAP.md) · [DECISIONS.md](DECISIONS.md) · [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: 2026-07-22

# Project Plan — Final Status

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Why decisions were made this way?** → [DECISIONS.md](DECISIONS.md)
- **Full change history?** → [CHANGELOG.md](CHANGELOG.md)

---

## Project Complete

This project set out to answer three research questions on the ADME public dataset (Fang et al. 2023): how training set size affects predictive performance, how much label noise ML models tolerate, and whether deep learning models show different noise sensitivity than classical models. All three phases below are complete.

---

## Phase 1 — Paper Recreation

**Notebooks**: `01.5_adme_biogen_public_recreation.ipynb`, `01.6_adme_paper_recreation_results.ipynb`

Reproduced Fang et al. (2023)'s methodology on the public ADME dataset as a validated baseline before running original experiments: same featurization (FCFP4, radius=2, 1024-bit), same 6 endpoints (HLM, MDR1, SOL, RLM, PPB_H, PPB_R), same `RepeatedKFold(5,3)` cross-validation. Extended from the paper's 5 models to 9 (added BayesianRidge, FCNN, MPNN1, MPNN2) with both baseline and tuned hyperparameter arms. Numerical deviations from the paper's published Table 2 were investigated and attributed to three specific, documented causes (unseeded RF/LightGBM in the paper's own script, a dedup-key mismatch, and single-draw split variance) — see `ADR-007` and `LESSONS_LEARNED.md` — none of which affect the paper's qualitative claims, which this recreation reproduces.

## Phase 2 — Supporting Analysis

**Notebooks**: `01.7_adme_mmp_analysis.ipynb`, `01.8_feature_selection.ipynb`, `01.9_stereochemistry_analysis.ipynb`

Matched molecular pair (MMP) analysis, feature selection diagnostics (RFE, shadow-feature tests, pruning-stage cost tracking), and a per-endpoint stereocentre/unassigned-stereo audit — supporting analyses that informed featurization and endpoint-modelling decisions used in Phases 1 and 3.

## Phase 3 — Data Quantity & Noise Experiments

**Notebooks**: `03_adme_data_quantity.ipynb`, `04_adme_noise.ipynb`, `05_dataset_size_comparison_viz.ipynb`

- **Data quantity**: learning-curve study across training set fractions on the paper-faithful pipeline, across models and featuresets.
- **Label noise**: noise injection study (Gaussian, systematic bias, gross errors — see `ADR-005`) parameterised in fold-error units, including a noise-ceiling/model-curve comparison.
- **Combined visualisation**: `05_dataset_size_comparison_viz.ipynb` presents the data-quantity and noise results together.

---

## Key Decisions

See [DECISIONS.md](DECISIONS.md) for the full architectural decision record (ADR-001 through ADR-012), covering missing-data handling, noise model definitions, hyperparameter tuning strategy, ChemProp/MPS constraints, and the paper-recreation methodology deviations.

---

**Last Updated**: 2026-09-01

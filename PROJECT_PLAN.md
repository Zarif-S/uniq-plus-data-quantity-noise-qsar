# Project Plan — Final Status

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Why decisions were made this way?** → [DECISIONS.md](DECISIONS.md)
- **Full change history?** → [CHANGELOG.md](CHANGELOG.md)

---

## Project Complete

This project began with three research questions about training set size and label noise on the ADME public dataset (Fang et al. 2023). Once underway, it took on a reproduction component — testing whether Fang et al.'s claims, developed on their confidential in-house dataset, held on their public release — and that work expanded to become the project's primary focus: claim-by-claim validation, statistical significance testing of model comparisons, sensitivity of the paper's claims to methodological choices, and feature selection. The original data-quantity/noise strand was deprioritised while the reproduction work grew, then revisited as a secondary strand once time allowed (Phase 3). All three phases below are complete.

---

## Phase 1 — Paper Recreation (primary focus)

**Notebooks**: `01.5_adme_biogen_public_recreation.ipynb`, `01.6_adme_paper_recreation_results.ipynb`

Reproduced Fang et al. (2023)'s methodology on the public ADME dataset as a validated baseline before running original experiments: same featurization (FCFP4, radius=2, 1024-bit), same 6 endpoints (HLM, MDR1, SOL, RLM, PPB_H, PPB_R), same `RepeatedKFold(5,3)` cross-validation. Extended from the paper's 5 models to 9 (added BayesianRidge, FCNN, MPNN1, MPNN2) with both baseline and tuned hyperparameter arms. Numerical deviations from the paper's published Table 2 were investigated and attributed to three specific, documented causes (unseeded RF/LightGBM in the paper's own script, a dedup-key mismatch, and single-draw split variance) — see `ADR-007` and `LESSONS_LEARNED.md` — none of which affect the paper's qualitative claims, which this recreation reproduces.

Beyond matching Table 2, `01.6` tested each of the paper's headline claims (non-RF > RF baseline; molecular representation matters more than algorithm choice; MAE decreases with test-set similarity to training) against the public data specifically, via paired one-way ANOVA + Tukey HSD on per-fold Pearson r, visualised as per-endpoint significance heatmaps. Results mostly held, with documented exceptions on the smaller public dataset (e.g. XGBoost underperforming RF on some endpoints, contrary to the paper) attributed to reduced statistical power at 3,087 vs 22,822 compounds. This sensitivity analysis — whether a paper's claims survive on a smaller, public substitute for its confidential data — was the project's most valuable contribution.

## Phase 2 — Supporting Analysis

**Notebooks**: `01.7_adme_mmp_analysis.ipynb`, `01.8_feature_selection.ipynb`, `01.9_stereochemistry_analysis.ipynb`

Matched molecular pair (MMP) analysis, a per-endpoint stereocentre/unassigned-stereo audit, and a staged feature selection pipeline (`01.8`) that reduced the paper's 50 RDKit descriptors (316 features once vector-valued ones are expanded) down through variance filtering, PCA/mutual-information scoring, CCA redundancy pruning, and VIF pruning to a LightGBM RFE sweep — landing on 2 descriptors (PEOE_VSA, SlogP_VSA) that retain 82% of the 48-descriptor baseline's mean cross-validated R² across the four core endpoints. These supporting analyses informed featurization and endpoint-modelling decisions used in Phases 1 and 3.

## Phase 3 — Data Quantity & Noise Experiments (secondary strand, revisited late)

**Notebooks**: `03_adme_data_quantity.ipynb`, `04_adme_noise.ipynb`, `05_dataset_size_comparison_viz.ipynb`

- **Data quantity**: learning-curve study across training set fractions on the paper-faithful pipeline, across models and featuresets.
- **Label noise**: noise injection study (Gaussian, systematic bias, gross errors — see `ADR-005`) parameterised in fold-error units, including a noise-ceiling/model-curve comparison.
- **Combined visualisation**: `05_dataset_size_comparison_viz.ipynb` presents the data-quantity and noise results together.

---

## Key Decisions

See [DECISIONS.md](DECISIONS.md) for the full architectural decision record (ADR-001 through ADR-012), covering missing-data handling, noise model definitions, hyperparameter tuning strategy, ChemProp/MPS constraints, and the paper-recreation methodology deviations.

---

**Last Updated**: 2026-09-02

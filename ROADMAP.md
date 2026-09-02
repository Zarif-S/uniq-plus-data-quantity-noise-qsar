# Roadmap - Strategic Vision

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Final status?** → [PROJECT_PLAN.md](PROJECT_PLAN.md)

---

## Known Discrepancies & Confirmed Methodology Notes

- **Fingerprint radius**: The Fang et al. (2023) paper text states "radius 4 (FCFP4)" — but these contradict each other. FCFP4 means diameter=4, which is radius=2. Their code (`ADME_ML_public.py` line 187) correctly uses `radius=2, nBits=1024, useFeatures=True`, i.e. FCFP4. The paper text confuses radius with diameter. We follow the code: radius=2, FCFP4.

- **Similarity metric**: Paper uses Sørensen-Dice coefficient (not Tanimoto) for all pairwise similarity calculations — confirmed in their methods section: *"structural similarity between any two samples was measured using the Sorensen−Dice coefficient based on FCFP4 fingerprints with a folding size of 1024 bits"*. Using Tanimoto gave 0.167 ± 0.059; switching to Dice gave **0.28 ± 0.08**, matching the paper exactly. Use `DataStructs.BulkDiceSimilarity` throughout.

- **Mol standardization**: Applied to every SDF mol before featurization, matching paper's `standardize()` exactly: Cleanup → FragmentParent → Uncharge → TautomerEnumerator.Canonicalize. This causes small compound losses vs CSV counts (1 per endpoint for HLM/MDR1/SOL/RLM) due to deduplication after canonical SMILES change — expected, paper would have encountered the same.

- **rdMolDes descriptor set**: Paper hand-picked 316 descriptors (`rdMolDes`) — not the full RDKit descriptor list. These are implemented in `src/features/features.py::rdmoldes()`. 9 of 316 are geometry-dependent and require SDF conformers (CalcPMI1/2/3, CalcAsphericity, etc.) — this is why SDF files are used rather than CSV SMILES.

- **MPNN featurization**: MPNN uses `rdkit_2d_normalized` (200 descriptors from descriptastorus) — a different set from rdMolDes (316). ChemProp calls descriptastorus internally; our `rdkit_2d_features()` does the same directly. All non-MPNN models use rdMolDes.

- **Cross-validation strategy**: Paper used `GridSearchCV` with `RepeatedKFold(n_splits=5, n_repeats=3, random_state=128)` for the public dataset — random fold assignment (not scaffold-based). Temporal splits not possible on public dataset (no time index).

- **Scaling**: RobustScaler applied for SVM, Lasso, FCNN only — fit_transform on X_train, transform on X_test. Not applied to RF, XGBoost, LightGBM (tree-based, scale-invariant). y values never scaled (already log-transformed in raw data).

---

## Project Complete

The project's strategic priority shifted partway through: the original vision was a data-quantity/noise study (below), but once reproduction work started, testing whether Fang et al.'s claims — built on their confidential dataset — held on the public release turned out to be more valuable and expanded to become the project's centre of gravity (Phase R1). Data quantity/noise was deprioritised while that expanded, then picked back up as a secondary strand once time allowed (Phase R2). Both phases are complete. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the final per-notebook status.

**Paper**: Fang et al. (2023) — *Prospective Validation of Machine Learning Algorithms for Absorption, Distribution, Metabolism, and Excretion Prediction: An Industrial Perspective*. DOI: 10.1021/acs.jcim.3c00160

---

## Phases

### Phase R1 — Paper Recreation (primary focus) (`01.5_adme_biogen_public_recreation.ipynb`, `01.6_adme_paper_recreation_results.ipynb`)

**Goal**: Match the paper's reported metrics as closely as possible using the same dataset, same endpoints, and (where described) the same models and splits, before designing original experiments on top — reproducing published results validates the pipeline, establishes baselines grounded in the literature and allows us to investigate how small changes in methodology affects the papers claims.

**Result**: Comparison table with paper vs reproduced metrics for all reported models/endpoints; deviations investigated and explained (see `ADR-007`, `LESSONS_LEARNED.md`). Beyond the metrics table, each headline claim (non-RF models beat RF; representation matters more than algorithm choice; MAE falls as test/train similarity rises) was re-tested for statistical significance (paired ANOVA + Tukey HSD) on the public data specifically — the question being whether conclusions drawn from a paper's public substitute dataset are as trustworthy as the ones drawn from its confidential original, since that public data is a foundation others (including this project) build on.

---

### Phase R2 — Original Experiments, revisited late (`03_adme_data_quantity.ipynb`, `04_adme_noise.ipynb`, `05_dataset_size_comparison_viz.ipynb`)

The learning curve (data quantity) and noise injection experiments — the project's original central strand — run on the paper-faithful pipeline established in Phase R1, once reproduction work concluded.

---

## Key Links

[PROJECT_PLAN.md](PROJECT_PLAN.md) · [DECISIONS.md](DECISIONS.md) · [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: 2026-09-02

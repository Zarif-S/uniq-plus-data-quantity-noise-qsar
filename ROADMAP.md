# Roadmap - Strategic Vision

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Current work?** → [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Previous roadmap (parked experiments)?** → [OLD_ROADMAP.md](OLD_ROADMAP.md)

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

## Current Focus: Reference Paper Recreation

**Goal**: Reproduce the published results from the reference paper (Biogen public ADME dataset) as faithfully as possible before designing original experiments on top.

**Why this first**: Reproducing published results validates our pipeline, confirms data handling is correct, and establishes credible baselines grounded in the literature. Any deviations from published numbers become a documented, explainable finding rather than an unknown bug.

**Paper**: Fang et al. (2023) — *Prospective Validation of Machine Learning Algorithms for Absorption, Distribution, Metabolism, and Excretion Prediction: An Industrial Perspective*. DOI: 10.1021/acs.jcim.3c00160

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

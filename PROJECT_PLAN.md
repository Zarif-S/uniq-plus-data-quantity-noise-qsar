# Project Plan - Tactical Execution

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Strategic vision?** → [ROADMAP.md](ROADMAP.md)
- **Previous plan (parked)?** → [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md)

---

## Current Focus

**Theme**: Recreating reference paper results on the Biogen public ADME dataset

**Notebook**: `notebooks/01.5_adme_biogen_public_recreation.ipynb`

---

## Now (In Progress)

**Phase R1 — Paper Recreation**

**Completed (2026-07-22)**
- [x] Document paper methodology — sections 1.1–1.5 in notebook (endpoints, split strategy, featurization, models, metrics)
- [x] Summary statistics — matches paper Table 2 for HLM, MDR1, SOL, RLM; PPB divergence explained (ChEMBL augmentation)
- [x] Pairwise Sørensen-Dice similarity — matches paper Fig 9 (mean=0.282 ± 0.083)
- [x] Preprocessing checks — criteria 1–4 verified or assumed pre-applied (see notebook 2.3)
- [x] SDF loading with mol standardization — `src/preprocessing/` module created, matches paper's standardize() exactly (4 steps: cleanup, fragment parent, uncharge, tautomer canonicalization); RDKit logs redirected to file rather than suppressed
- [x] Featurization complete — FCFP4 (1024), rdMolDes (316), hybrid (1340), rdkit_2d_normalized (200); all stored in feat[ep] per endpoint
- [x] Workflow diagram written — `workflow_diagrams/01.5_adme_biogen_public_receration.txt`

**Up Next**
- [ ] Section 4 — Models & splits: GridSearchCV with RepeatedKFold(n_splits=5, n_repeats=3); RF, XGBoost, LightGBM, SVM, Lasso per feature set; RobustScaler fit_transform on X_train / transform on X_test for SVM and Lasso
- [ ] Section 4 — MPNN: ChemProp with rdkit_2d_normalized (already in feat[ep] as rdkit_norm)
- [ ] Section 4 — Requires paper's train/test split files (TODO: Zarif to add to data/raw/)
- [ ] Section 5 — Comparison table: paper Pearson r vs reproduced values per model per endpoint; document deviations

---

## Parked

**Original experiments** (learning curves, noise injection, 2D grid, Phase 5b) — see [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md) and [OLD_ROADMAP.md](OLD_ROADMAP.md) for full design. All `src/` modules and data remain intact.

---

## Key Links

[ROADMAP.md](ROADMAP.md) · [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md) · [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: 2026-07-22

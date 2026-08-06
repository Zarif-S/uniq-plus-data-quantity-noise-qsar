# Project Plan - Tactical Execution

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Strategic vision?** → [ROADMAP.md](ROADMAP.md)
- **Previous plan (parked)?** → [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md)

---

## Current Focus

**Theme**: Recreating reference paper results on the Biogen public ADME dataset — now extending from 5 to 9 models (adding BayesianRidge, FCNN, MPNN1, MPNN3) plus hyperparameter tuning for all of them.

**Live working notebook**: `notebooks/01.5_adme_biogen_public_recreation.ipynb` (has plots — heavy to read wholesale; pull cell `source` only, not `outputs`, when reviewing)
**Lightweight reference copy** (no plots, used for design discussion): `notebooks/01.5_adme_biogen_public_recreation_adding_models_hyperpam_tuning.ipynb` — currently missing the hyperparameter-tuning design notes agreed below; keep in sync manually or treat as secondary.

---

## Now (In Progress)

**Phase R1 — Paper Recreation**

**Completed (2026-07-22)**
- [x] Document paper methodology — sections 1.1–1.5 in notebook (endpoints, split strategy, featurization, models, metrics)
- [x] Summary statistics — matches paper Table 2 for HLM, MDR1, SOL, RLM; PPB divergence explained (ChEMBL augmentation)
- [x] Pairwise Sørensen-Dice similarity — matches paper Fig 9 (mean=0.282 ± 0.083)
- [x] Preprocessing checks — criteria 1–4 verified or assumed pre-applied (see notebook 2.3)
- [x] SDF loading with mol standardization — `src/preprocessing/` module created, matches paper's standardize() exactly (4 steps: cleanup, fragment parent, uncharge, tautomer canonicalization); RDKit logs redirected to file rather than suppressed
- [x] Featurization — FCFP4 (1024), rdMolDes (316), hybrid (1340); `rdkit_2d_normalized` (200, descriptastorus) computed but **now planned for removal** — see Section 3 note below
- [x] Workflow diagram written — `workflow_diagrams/01.5_adme_biogen_public_receration.txt`

**Completed (2026-07-28)**
- [x] Section 4.1/4.2 — RF, XGBoost, LightGBM, SVM, Lasso implemented (`src/models/paper_models.py`: `get_paper_models`, `tune_paper_model`, `model_validation`); `arm='base'` run and persisted (`data/processed/section4_splits.pkl`, `section4_paper_recreation_results.csv`, `section4_test_predictions.pkl`)
- [x] Section 5.1–5.5 — MAE/Pearson summary tables, per-model boxplots, similarity-binned MAE (Dice/Tanimoto), ANOVA + Tukey HSD — all on `arm='base'`, `hybrid` featureset
- [x] Full design discussion for the 4 new models + tuning strategy — see spec below

---

## Up Next

### Architecture decision (2026-07-29): decouple tuning from eval + checkpoint the eval loop

Agreed approach for extending Section 4 to 9 models + tuning:

- **Keep tuning decoupled from eval** (the plan's original choice): the base eval loop (4.2) and the tuning pass (4.4) stay separate cells. Reinforced by the fact that the tuners are *heterogeneous* — staged `GridSearchCV` (classical), a `for`-loop over `FCNN_ARCHITECTURES` (FCNN), and `hyperopt.fmin` TPE (MPNN1/2) — so an inline `arm='tuned'` flag inside the eval loop would jam 3–4 unrelated control-flows into one loop body. Decoupling lets each tuner be organized per model-family and emit cached params/configs that the eval loop consumes uniformly.
- **Add Option C — checkpointed, resumable eval loop**: a shared helper skips any `(ep, fs, model, arm)` key already present on disk, else computes → appends → persists incrementally. This targets the real cost (the base loop is 60 combos × 16 fits = **960 model fits**, ~30–60 min) so that adding one heavy new model, or re-running one endpoint, only computes the missing keys instead of the whole grid. Crash-safe. Both the 4.2 base loop and the 4.4 tuned pass reuse the same helper.
  - *Discipline required*: cache invalidation is manual — when a model's definition changes, clear its rows / bump a key, or stale results persist silently.

**Cost reference** (measured from `section4_paper_recreation_results.csv`): base arm = 4 endpoints × 3 featuresets (`fcfp4`/`rdkit`/`hybrid`) × 5 models = 60 combos; each `model_validation` = 15 `RepeatedKFold(5,3)` fold-fits + 1 final refit = 16 fits → 960 total. RF/XGB/LightGBM each fit 500 trees.

**`n_jobs` note**: base models RF/XGB set `n_jobs=-1` and LightGBM defaults to `-1`; on a 10-core machine, stacking `cross_val_score(n_jobs=-1)` on top nests parallelism (~100 threads). `n_jobs_cv=2` is a safe compromise; the more predictable config is models `n_jobs=1` + `n_jobs_cv=-1` (fold-level parallelism, no nesting). Not blocking — deferred, no retime for now.

**Agreed execution order:**
1. ✅ **Checkpointing refactor** (done 2026-07-29) — `load_eval_checkpoint`, `run_checkpointed_eval`, `invalidate_checkpoint` in `src/models/paper_models.py` (+11 tests); notebook loop rewritten as `compute_one` closure + `keys` list. `invalidate_checkpoint(RESULTS_CSV, PREDICTIONS_PKL, model='RF')` drops matching keys from both files for targeted recompute.
2. ✅ **Add BayesianRidge** (done 2026-07-29) — in `get_paper_models()` (deterministic, RobustScaler branch alongside SVM/Lasso); `param_base_BayesianRidge` now exported from `src.hyperparams`. Verified: appends 12 base keys (r 0.51–0.72, hybrid>rdkit>fcfp4). **Real `data/processed/` files not yet repopulated — run the Section 4.2 loop cell to append them (~1 min).**
3. **Add FCNN + MPNN1/MPNN3 wrappers** — the real work (new sklearn-compatible estimator classes); base loop appends their rows incrementally.
   - ✅ **FCNN** (done 2026-07-29) — `src/models/fcnn.py` (`FCNN(BaseEstimator, RegressorMixin)` wrapping DeepChem `MultitaskRegressor`, lazy DeepChem/torch imports); added to `get_paper_models()` (scaled-features branch alongside SVM/Lasso/BayesianRidge) and the notebook scaling branch; `param_base_FCNN` exported. Verified through `model_validation` (HLM/hybrid: CV r=0.692, test r=0.744, MAE=0.321). +6 tests (`tests/test_fcnn.py`). Decisions (2026-07-29): **batch_norm dropped** — DeepChem 2.8.0 MultitaskRegressor has no BN, accepted-but-warned; **Adam "alpha"→beta1=0.9** wired via explicit `dc.models.optimizers.Adam(lr, beta1)` and recorded in `param_base_FCNN`; the `param_base_FCNN` trailing-comma tuple bug was fixed by the user. `weight_init_stddevs=[0.02]` (1-elem list) collapses to scalar 0.02 to avoid single-layer collapse.
   - ✅ **MPNN1 + MPNN3 wrapper** (done 2026-07-29) — `src/models/mpnn.py`: one `ChempropRegressor(BaseEstimator, RegressorMixin)` over ChemProp 1.6.1's Python API (`TrainArgs().parse_args` + `cross_validate(train_func=run_training)` + `make_predictions`, data via temp CSVs; ChemProp/torch imported lazily). `use_features=False` → MPNN1 (graph-only); `use_features=True` → MPNN3. Exported from `src/models`; `param_base_MPNN` exported from `src.hyperparams`. +7 tests (`tests/test_mpnn.py`). Verified on real HLM (30 epochs): MPNN1 r=0.663/MAE=0.356, MPNN3 r=0.675/MAE=0.369 — in line with the classical models. Decisions (2026-07-29):
     - **Validation** — the paper (`MPNN_public.py`, confirmed via GitHub) did a *single split, no CV, single Pearson r*. We deliberately deviate to get a boxplot distribution: MPNN runs through the same `model_validation()` as the others (it's a sklearn estimator), with a **Full/Sample flag** setting `n_splits`/`n_repeats`. Proposed `MPNN_CV = {'full': dict(n_splits=5, n_repeats=3, epochs=30) ~100min, 'sample': dict(n_splits=2, n_repeats=1, epochs=20) ~10min preview}` — Sample is an undertrained *preview*, not comparable to Full.
     - **MPNN3 features** — rmoldes 316 (the `'rdkit'` featureset's RobustScaler'd matrix) via ChemProp `--features_path` + `--no_features_scaling`; deviates from paper's `rdkit_2d_normalized`.
     - **X-encoding** — SMILES packed into `X` so `cross_val_score` row-splits keep SMILES+features aligned: MPNN1 `X=(n,1)`; MPNN3 `X=(n,1+316)` object array (col 0 = SMILES).
     - **`--num_workers 0`** — required: DataLoader worker spawn breaks under Jupyter/stdin and would nest inside sklearn CV parallelism. (Also *unlocks* optional fold-level parallelism as a future speedup.)
   - ✅ **Notebook MPNN integration** (done 2026-07-30) — new **Section 4.2b** cell (notebook cells `mpnn42b_md`/`mpnn42b_code`, inserted after the 4.2 loop). Builds 8 keys (MPNN1 `fs='graph'` + MPNN3 `fs='graph_rdkit'`, × 4 endpoints); `compute_one_mpnn(key)` reads SMILES/y from the `fcfp4` split (identical across featuresets for an endpoint) and rmoldes features from the `rdkit` split, clones `ChempropRegressor(**param_base_MPNN, use_features=…, epochs=MPNN_CV[MPNN_MODE]['epochs'])`, and runs `model_validation(…, n_splits/n_repeats from MPNN_CV[MPNN_MODE], n_jobs=1)`; appends to the same `section4_*` checkpoint via `run_checkpointed_eval`, so Section 5 picks them up automatically. `MPNN_MODE` flag (`'sample'` = 2×1/20ep preview, `'full'` = 5×3/30ep) is set inline in the cell. Cell 4 imports extended (`ChempropRegressor`, `param_base_MPNN`). Verified against real splits + temp checkpoint (2ep smoke): MPNN1 r_test=0.34, MPNN3 r_test=0.59, cv_scores len matches folds, re-run skips both keys. **Real `data/processed/` files not yet repopulated — run the 4.2b cell to append them (`'sample'` ~10 min / `'full'` ~100 min).**
     - **Mode persistence + supersede policy** (resolved 2026-07-30) — the row now records a `mpnn_mode` column (NaN for classical models), and `'full'` supersedes `'sample'`: before running, any existing MPNN key whose stored mode ranks *weaker* than the current `MPNN_MODE` is `invalidate_checkpoint`'d so it recomputes, while equal-or-stronger keys skip. So a cheap `'sample'` preview never blocks a later `'full'` run, and re-running `'sample'` never clobbers an existing `'full'` result. Verified sample→full (recomputes)→sample (no clobber, stays 2 rows).
4. **Section 4.4 tuning pass** — heterogeneous tuners, decoupled (MPNN tuner = `hyperopt.fmin` TPE, per earlier spec).

#### Section 5 wiring for the new models (done 2026-07-30, developed against a dummy-data harness)
New **Section 5.0 dummy-data harness** cell (`sec5_dummy_*`, toggle `USE_DUMMY_SECTION5`) — synthesises a schema-exact `results_df`/`predictions` (all 9 models, MPNN under `graph`/`graph_rdkit`, `mpnn_mode` col, 15-fold `cv_scores`) from the real `splits`, so Section 5 plots can be built before the overnight run. Wired the model lists per user's per-figure spec:
- **5.1/5.2 tables** — auto-include all models/featuresets (no edit); table is wider/sparser (MPNN only under graph featuresets).
- **5.3** (per-model boxplot, hybrid) — added BayesianRidge + FCNN. MPNN can't appear (no hybrid preds).
- **5.3b** (Fig 5, representation effect) — added FCNN + BayesianRidge. MPNN excluded by design.
- **5.4** (Fig 6, similarity-binned MAE) — added MPNN3 + BayesianRidge; `sim_fs_for()` resolves each model's featureset (MPNN3 → `graph_rdkit`); subplot grid now scales with model count.
- **5.5** (ANOVA/Tukey) — added MPNN1 + MPNN3 (skipped BayesianRidge). `build_cv_long_df` now takes a per-model featureset map + a **fold-count guard**: it keeps only models on the shared 15-fold `RepeatedKFold(random_state=128)` grid and returns the kept list (`ANOVA_MODELS`), which downstream cells iterate. **MPNN joins 5.5 only after a `'full'` run** — 3 folds does *not* help (unpaired partitions; needs the identical 5×3/rs=128 grid); under `'sample'` MPNN is auto-dropped and the ANOVA still runs on the classical models. Verified full (6 models) + sample (MPNN dropped) paths headlessly.
- ✅ **5.3** now also includes MPNN1/MPNN3 (done 2026-07-30) via a `BOXPLOT_MODEL_FS` resolver — each MPNN shown at its own `graph`/`graph_rdkit` featureset (no `hybrid` preds), suptitle annotated.
- ✅ **5.7 — Table 2 recreation** (done 2026-07-30, cell `table2_57_code`) — top block = §2.1 summary stats (all 6 endpoints); bottom block = per-model Pearson r as `CV_r (test_r)`, rows `R (model)ᵇ` (base) / `R (model)ᶜ` (tuned), models RF/LightGBM/MPNN1/MPNN3. `TABLE2_CLASSICAL_FS='hybrid'` knob for RF/LightGBM featureset; MPNN reads `graph`/`graph_rdkit`. ᶜ rows blank until the `tuned` arm exists; hPPB/rPPB show stats only (unmodelled). Deviations documented: CV_r = mean RepeatedKFold(5×3) not single 5-fold. Verified against dummy `results_df`.
- ✅ **5.6 — Figure 7 recreation** (done 2026-07-30, cell `fig7_56_code`) — 1×3 grouped bar charts (RF, LightGBM, MPNN3), x=endpoints (HLM/MDR1/SOL/RLM; PPB omitted), two bars each: **default** (`base` arm) vs **optimized** (`tuned` arm), y=test-set Pearson r. RF/LightGBM use `FIG7_CLASSICAL_FS='hybrid'`; MPNN3 uses `graph_rdkit`. **Error bars = bootstrap SD of the test-set Pearson r** (resample test compounds, `N_BOOT=1000`, set 0 to disable) — the paper's error source is unstated, this is a principled test-metric uncertainty. Optimized bars stay empty (`nan`) until the `tuned` arm is run, then fill automatically. Verified headlessly (Agg) against dummy data.

**Section 5 is now fully wired for all 9 models across 5.1–5.7.** Remaining Section 5 dependency: the `tuned` arm (Section 4.4) to populate 5.6's optimized bars + Table 2's ᶜ rows, and a `'full'` MPNN run to admit MPNN into 5.5's ANOVA.

### 1. Add 4 new models to `get_paper_models()`

| Model | Features | Scaling | Wrapper | Base hyperparams |
|---|---|---|---|---|
| **BayesianRidge** | fcfp4 / rdmoldes / hybrid | RobustScaler (same list as SVM/Lasso) | plain sklearn `BayesianRidge()` | `param_base_BayesianRidge = {}` |
| **FCNN** | fcfp4 / rdmoldes / hybrid | RobustScaler | new sklearn-compatible wrapper around DeepChem `MultitaskRegressor` | `param_base_FCNN`: lr 0.001, Adam, batch_norm=True, weight_decay=0.0004 (L2), batch_size=128, ReLU, epochs=50, `bias_init_consts=1.0`, `weight_init_stddevs=0.02` (confirmed in `FCNN_public.py`, missing from Table S15 — include anyway) |
| **MPNN1** | graph (SMILES) only | none | new `ChempropRegressor(BaseEstimator, RegressorMixin)` wrapper, chemprop Python API (not CLI subprocess) | chemprop defaults: `hidden_size=300, depth=3, dropout=0.0, ffn_num_layers=2` |
| **MPNN3** | graph + rmoldes (316, scaled) | rmoldes side reuses the existing `'rdkit'` split's RobustScaler from Section 4.1 | same `ChempropRegressor`, `use_rdkit_features=True`, external features passed via chemprop's features-array mechanism (not `features_generator='rdkit_2d_normalized'`) | same as MPNN1 |

- [ ] `hyperparams.py`: add `param_base_BayesianRidge`, `param_base_FCNN`, `param_base_MPNN`
- [ ] `hyperparams.py`: add `FCNN_ARCHITECTURES` lookup — **5 presets from Table S15 only** (the 6th, `[2000,1000,500]`/`[0.25,0.25,0.10]`, exists in `FCNN_public.py` but isn't documented in the SI table — excluded for traceability)
- [ ] Drop `rdkit_2d_features`/descriptastorus usage from Section 3 — MPNN3 no longer needs it now that it reuses the `'rdkit'` (rmoldes) featureset; leave the function in `src/features/features.py` unused rather than deleting
- [ ] Re-run Section 4.2's `arm='base'` loop to cover all 9 models (currently only has the original 5)

### 2. Section 4.4 — separate hyperparameter tuning pass (design agreed 2026-07-30)

Deliberately **not** inline with Section 4.2's loop — the tuners are heterogeneous and heavy. **Two resumable layers**, both crash-safe:

```
4.4a  TUNE (expensive) → best-params cache:  for each (endpoint, featureset in TUNE_FEATURESETS, model)
        classical → tune_paper_model (staged GridSearchCV, already exists)
        FCNN      → tune_fcnn_architecture (new: CV-score the 5 FCNN_ARCHITECTURES, keep best)
        MPNN1/2   → ChemProp's BUILT-IN hyperopt (new wrapper: TPE over its default 4D space)
      → write best_params to data/processed/section4_tuned_params.json, keyed 'endpoint|featureset|model'
        (skip keys already in the cache — resumable). Reuse src/tuning save_params/load_params.
4.4b  EVAL (reuses 4.2/4.2b machinery):  build each model from its cached best_params →
        model_validation → arm='tuned' → run_checkpointed_eval into the same section4_* files.
```

- **`TUNE_FEATURESETS` flag** — `['hybrid']` for day-to-day (covers Fig 7 / Table 2), all three `FEATURESETS` for the overnight run.
- **MPNN Full/Sample flag** also governs tuning cost: `num_iters` for ChemProp hyperopt (full ≈ 20 matching `chemprop_hyperopt --num_iters 20`, sample ≈ 3 preview) and the CV grid of the follow-up `model_validation`.

| Model(s) | Tuning method | Notes |
|---|---|---|
| RF, XGBoost, LightGBM, SVM, Lasso | existing `tune_paper_model` + `PARAM_GRID_STAGES` (`GridSearchCV(cv=5)`, plain `KFold`) | paper's real method; RF/SVM/Lasso single-stage joint grids, XGBoost (5)/LightGBM (4) sequential/greedy |
| BayesianRidge | none | not in the 4.4 model set (deterministic); if a `'tuned'` row is ever wanted it reuses the `'base'` result verbatim |
| FCNN | new `tune_fcnn_architecture()`: `model_validation()` per candidate in `FCNN_ARCHITECTURES` (5), keep best **train-only** `Pearson_r_CV` | picking via train-only CV avoids the test-leakage of eyeballing `r_test` (paper's own script does no formal selection) |
| MPNN1, MPNN3 | new wrapper around **ChemProp's built-in hyperopt** (TPE over `{hidden_size, depth, dropout, ffn_num_layers}` — its default space = paper's S14), `num_iters` by Full/Sample | use ChemProp's own `hyperparameter_optimization`, not a hand-rolled `hyperopt.fmin`; `hyperopt` already installed (chemprop transitive dep) |

- [ ] Export `FCNN_ARCHITECTURES` from `src.hyperparams` (currently defined but unexported)
- [ ] `"FCNN"`/`"MPNN*"` stay out of `PARAM_GRID_STAGES` (that dict is `GridSearchCV`-specific)

### 3. Downstream — Section 5 (DONE 2026-07-30, populates after 4.4)

- ✅ Section 5.6 — **Figure 7** (default-vs-optimized test-r bar charts, cell `fig7_56_code`); optimized bars fill once the `tuned` arm exists.
- ✅ Section 5.7 — **Table 2** (`CV_r (test_r)`, ᵇ base / ᶜ tuned, cell `table2_57_code`); ᶜ rows fill once the `tuned` arm exists.
- [ ] Section 4.3 — Scaffold split (parked, unrelated to this work)

### Deferred — revisit only if needed

FCNN has no early stopping (fixed 50 epochs, matches the paper); MPNN's early stopping is a single internal chemprop train/val/test split, not k-fold — both are lower-rigor than the classical models' 5-fold `GridSearchCV` + the `RepeatedKFold(5,3)` diagnostic every model gets via `model_validation()`. If FCNN/MPNN underperform the classical models on the public set (paper's own public-set numbers may have the same rigor gap vs. their in-house temporal-split numbers), consider adding real early-stopping for FCNN and/or more extensive CV for both — not blocking initial implementation.

---

## Parked

**Original experiments** (learning curves, noise injection, 2D grid, Phase 5b) — see [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md) and [OLD_ROADMAP.md](OLD_ROADMAP.md) for full design. All `src/` modules and data remain intact.

---

## Key Links

[ROADMAP.md](ROADMAP.md) · [OLD_PROJECT_PLAN.md](OLD_PROJECT_PLAN.md) · [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: 2026-07-29

# Synchronizations - UNIQ+

This document defines all cross-concept pipeline handoffs.

**Rule**: If an action coordinates between two or more concepts (pipeline stages), it belongs here — not inside any individual concept. Concepts must remain independent; this file is the only place where inter-concept relationships are expressed.

---

## How to Read This Document

Each entry follows the pattern from Meng & Jackson (2025):

> **When** `[ConceptA].[action]` fires, **if** [condition], **then** `[ConceptB].[action]` follows.

For this project, "concepts" are the major pipeline stages: `Data`, `EDA`, `Splitting`, `Featurization`, `Model`, `Results`, `Noise` (Phase 2).

---

## Synchronizations

### [SYNC-001] Data loading triggers EDA profiling

**Trigger**: `Data.load(dataset_path, endpoint)`

**Condition**: Always

**Effects**:
- `EDA.profile(dataframe)` — produces distribution plots, SMILES validity check, missing value report, endpoint summary statistics

**Rationale**: EDA must run on the raw loaded dataframe before any cleaning decisions are made. Neither concept should know about the other; the handoff ensures EDA always sees unmodified data.

---

### [SYNC-002] EDA findings gate data cleaning

**Trigger**: `EDA.profile(dataframe)`

**Condition**: Invalid SMILES or missing endpoint values are present in the profiling report

**Effects**:
- `Cleaning.filter_endpoint(dataframe, endpoint_col)` — per-endpoint NaN filtering; each model trains only on rows with a non-NaN value for its target endpoint

**Decision** (2026-07-13): Per-endpoint filtering. Complete-case filtering rejected (retains only ~180 rows due to PPB 94–95% missingness). Imputation rejected (missing values are structural — compounds were never sent to assay, not randomly missing). See ADR-002 in DECISIONS.md.

**Rationale**: Cleaning decisions depend on what EDA reveals — the strategy cannot be hardcoded in advance. This sync makes the dependency explicit and forces a conscious decision before proceeding to splitting.

---

### [SYNC-003] Cleaned data triggers train/test splitting

**Trigger**: `Data.clean(dataframe)`

**Condition**: Split strategy must be explicitly chosen before this handoff (random / scaffold / temporal). Strategy is passed as a parameter — never defaulted silently.

**Effects**:
- `Splitting.split(dataframe, strategy, seed)` — returns `(train_df, test_df)` with the strategy recorded in the split metadata

**Rationale**: The split strategy is a key experimental decision that affects all downstream results. Formalising it here prevents it from being buried in notebook code and ensures it is always explicit and reproducible.

---

### [SYNC-004] Split triggers featurization on train and test separately

**Trigger**: `Splitting.split(dataframe)` → produces `(train_df, test_df)`

**Condition**: Featurizer (scaler / normalizer, if used) must be fit on `train_df` only, then applied to both. Morgan fingerprints require no fitting step — compute directly on both sets. Violation of this condition introduces data leakage.

**Effects**:
- `Featurization.fit_transform(train_df)` → `(X_train, y_train)`
- `Featurization.transform(test_df)` → `(X_test, y_test)`

**Rationale**: Featurization must occur after splitting to prevent leakage. Test data must never influence the featurizer. These two concepts are kept separate so that featurization logic cannot accidentally access the full dataset.

---

### [SYNC-005] Featurized data triggers model training

**Trigger**: `Featurization.fit_transform(train_df)` and `Featurization.transform(test_df)`

**Condition**: Always — `X_train`, `y_train`, `X_test`, `y_test` all present

**Effects**:
- `Model.train(X_train, y_train, model_name)` → fitted model, where `model_name` ∈ {`LinearRegression`, `BayesianRidge`, `RandomForest`, `XGBoost`, `LightGBM`}

**Rationale**: Model training can only begin once both splits are featurized and isolated. Keeping this as an explicit handoff prevents premature training on un-split or un-featurized data. BayesianRidge is included as the Bayesian baseline (see ADR-001); LinearRegression as the interpretable baseline.

---

### [SYNC-006] Trained model triggers evaluation and results

**Trigger**: `Model.train(X_train, y_train)` → fitted model

**Condition**: Always

**Effects**:
- `Results.evaluate(model, X_test, y_test)` → metrics dict (R², RMSE)
- `Results.plot(y_test, y_pred)` → predicted vs actual plot

**Rationale**: Evaluation must always use the held-out test set produced by SYNC-003/SYNC-004. Separating Results from Model ensures evaluation logic is reusable across model types and not tangled with training code.

---

### [SYNC-007] Pre-defined split columns bypass split generation for PDE10A

**Trigger**: `Cleaning.filter_endpoint(df, "pic50")` → cleaned PDE10A DataFrame

**Condition**: The cleaned DataFrame contains one or more columns from `Splitting.SPLIT_COLS` (i.e., it is PDE10A data with pre-assigned split labels)

**Effects**:
- For each `split_col` in `Splitting.SPLIT_COLS`: `Splitting.get_split(df, split_col)` → `(train_df, test_df)`
- The loop over split columns produces 7 independent `(train_df, test_df)` pairs, each fed into SYNC-004 → SYNC-006 separately
- `val` rows are discarded by `get_split` and never reach featurization or model training

**Rationale**: PDE10A splits encode temporal, chemotype, and random strategies pre-assigned by the dataset authors — generating splits with sklearn would destroy this scientific structure. `Cleaning` must remain ignorant of how splits will be applied; `Splitting` must remain ignorant of why the labels are pre-defined. This SYNC makes explicit that the Cleaning→Splitting handoff uses column-filter semantics (not split generation) when `SPLIT_COLS` columns are present, and that the downstream pipeline runs independently for each of the 7 strategies. SYNC-003 (random split generation) applies to ADME only; this entry applies to PDE10A only.

---

## Reference

### Pipeline stage concepts

| Concept | Responsibility |
|---|---|
| `Data` | Loading raw CSVs, cleaning, exposing dataframes |
| `EDA` | Profiling, distribution plots, validity checks |
| `Splitting` | Train/test splitting with explicit strategy selection |
| `Featurization` | SMILES → fingerprints/descriptors; fit on train only |
| `Model` | Training and cross-validation of RF/XGB/LGB models |
| `Results` | Metrics, predicted vs actual plots, learning curves |
| `Splitting` | Train/test extraction from pre-defined CSV split columns (PDE10A); random split generation (ADME, inline) |
| `Noise` | Label noise injection (Phase 2 — not yet active) |

### What belongs here vs. inside a concept

| Belongs in concept code / CLAUDE.md | Belongs here |
|---|---|
| Internal logic of a single stage | Handoffs between stages |
| Validation of own inputs | Leakage guards spanning two stages |
| Stage-specific parameters | Cross-stage parameter contracts |
| Own error handling | Conditions that gate downstream work |

### When to add a new synchronization

- An action in one stage produces outputs consumed by another stage
- A safety constraint (e.g. leakage guard) spans two stages
- A decision must be made explicit before a handoff can proceed

---

**Last Updated**: 2026-07-13 (SYNC-007 added)

**Related**: [ROADMAP.md](ROADMAP.md) · [PROJECT_PLAN.md](PROJECT_PLAN.md) · [CLAUDE.md](CLAUDE.md)

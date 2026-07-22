# src/ — Module Index

Reusable Python modules imported by notebooks. Each module is a subpackage with its own `CLAUDE.md`.

---

## Modules

| Module | Role | CLAUDE.md |
|--------|------|-----------|
| `eda` | Quality checks on raw molecular data (SMILES validity, missing values) | [eda/CLAUDE.md](eda/CLAUDE.md) |
| `features` | SMILES → ML-ready features (RDKit descriptors, fingerprints) | [features/CLAUDE.md](features/CLAUDE.md) |
| `plotting` | Reusable visualisations (endpoint distributions, learning curves) | [plotting/CLAUDE.md](plotting/CLAUDE.md) |
| `cleaning` | Per-endpoint NaN filtering and IQR outlier detection | [cleaning/CLAUDE.md](cleaning/CLAUDE.md) |
| `models` | Baseline model factory and uniform evaluation utilities | [models/CLAUDE.md](models/CLAUDE.md) |
| `splitting` | Pre-defined train/test splits from PDE10A CSV columns (7 strategies) | [splitting/CLAUDE.md](splitting/CLAUDE.md) |
| `tuning` | Hyperparameter tuning (LightGBM, RF) + frozen param management | [tuning/CLAUDE.md](tuning/CLAUDE.md) |
| `noise` | Label noise injection (Gaussian, systematic bias, gross errors) | [noise/CLAUDE.md](noise/CLAUDE.md) |

---

> **Isolation rule**: Each submodule CLAUDE.md describes only what that concept owns. Any coordination between modules belongs in [SYNCHRONIZATIONS.md](../SYNCHRONIZATIONS.md) — not in individual module docs.

---

## Concept Specification

**Purpose**: Provide a set of stateless, composable Python functions that transform raw molecular data into model-ready features, predictions, and visualisations — with each submodule owning a single stage of the pipeline.

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless index)* | — | This file is a navigation index; all state is held within individual submodules |

### Actions

Entry points per submodule:

| Submodule | Key entry points |
|-----------|-----------------|
| `eda` | `smiles_validity_report`, `missing_value_report`, `max_corr_report` |
| `features` | `morgan_fingerprints`, `rdkit_descriptors` |
| `plotting` | `endpoint_distributions`, `pred_vs_actual_grid` |
| `cleaning` | `filter_endpoint`, `flag_iqr_outliers`, `exclude_stereoisomer_pairs` |
| `models` | `get_baseline_models`, `evaluate_model` |
| `splitting` | `get_split`, `list_split_cols` |
| `tuning` | `tune_lightgbm`, `tune_rf`, `make_model`, `save_params`, `load_params` |
| `noise` | `add_gaussian_noise`, `add_systematic_bias`, `add_gross_errors` |

### Invariants

- All modules accept molecular data via a pandas DataFrame (SMILES as a column) or a list of SMILES strings
- No module modifies raw data — inputs are never mutated
- All functions are stateless: same inputs always produce same outputs
- `src/__init__.py` does NOT exist (namespace packages; adding one would break imports)

---

## Architecture

```
raw data
   │
   ▼
[eda] — SMILES validity + missing value reports
   │
   ▼
[cleaning] — per-endpoint NaN filter + IQR outlier flagging
   │
   ▼
[splitting] — apply pre-defined train/test split column (PDE10A); or inline sklearn split (ADME)
   │
   ▼
[features] — SMILES → fingerprints / descriptors
   │
   ▼
[models] — fit baselines, evaluate (R², RMSE, MSE)
   │
   ▼
[tuning] — tune LightGBM/RF (RandomizedSearchCV), freeze params to JSON
   │
   ▼
[noise] — inject Gaussian / systematic / gross-error noise into y_train
   │
   ▼
[plotting] — visualise distributions, predicted vs actual
```

---

## Breadcrumbs

- **Project setup** → [Root CLAUDE.md](../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../PROJECT_PLAN.md)

---

**Last Updated**: 2026-07-20

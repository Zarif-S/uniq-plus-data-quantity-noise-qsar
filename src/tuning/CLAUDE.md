# Tuning — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Tune LightGBM, RandomForest, and MPNN2 hyperparameters via RandomizedSearchCV, and provide utilities for saving/loading params. Used both for clean-data baseline tuning (Phase 3) and re-tuning under each experimental condition (Phases 4–6).

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless)* | — | All functions are pure; tuned parameters are returned and stored by the caller |
| `LGBM_PARAM_GRID` | `dict` | Default search space for LightGBM (6 hyperparams) |
| `RF_PARAM_GRID` | `dict` | Default search space for RandomForest (4 hyperparams) |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `tune_lightgbm` | `(X_train, y_train, X_val, y_val, param_grid=None, n_iter=50, random_state=42) → (fitted_model, best_params)` | RandomizedSearchCV with PredefinedSplit (fixed val set); refits on train+val before returning |
| `tune_rf` | `(X_train, y_train, X_val, y_val, param_grid=None, n_iter=50, random_state=42) → (fitted_model, best_params)` | Same pattern for RandomForest |
| `make_model` | `(model_name, params) → unfitted_estimator` | Create unfitted model from params dict (used in baseline arm of experiment loop) |
| `save_params` | `(params, path) → None` | Serialise hyperparameter dict to JSON |
| `load_params` | `(path) → dict` | Load hyperparameter dict from JSON |

### Invariants

- Tuning uses only training data — the test set is never seen during parameter search
- A fixed 20% val set is carved from `X_train` in the notebook before calling `tune_*`; the function uses `PredefinedSplit` so the same molecules are always held out
- After selecting best params, the model is refitted on the full `X_train + X_val` before returning (refit on all available training data)
- Clean-data tuned parameters are serialised to `models/tuned_params/{endpoint}_{model}.json` as a reference
- In the experiment loop (Phases 4–6), tuning is re-run per condition for the tuned arm; baseline arm uses default hyperparameters
- MPNN2 is tuned via early stopping (fixed architecture, generous epochs), not grid search
- The same `random_state=42` seed used throughout the project applies here
- `make_model` raises `ValueError` for unknown model names

---

## Architecture

```
Phase 3: Clean-data baseline tuning
        │
        ├──→ tune_lightgbm(X_train_tune, y_train_tune, X_val, y_val)
        │         RandomizedSearchCV + PredefinedSplit (n_iter=50, fixed val set)
        │         → refit on X_train_tune + X_val
        │         → (fitted_model, best_params)
        │         → save_params → models/tuned_params/{ep}_lgbm.json
        │
        ├──→ tune_rf(X_train_tune, y_train_tune, X_val, y_val)
        │         → save_params → models/tuned_params/{ep}_rf.json
        │
        └──→ MPNN2: ChemProp early stopping
                  Fixed architecture, --epochs 50

Phase 4–6: Experiment loop (per condition)
        │
        ├──→ Baseline arm:
        │         LGBMRegressor(**defaults).fit(X_sub, y_noisy)
        │         → evaluate on clean test
        │
        └──→ Tuned arm:
                  tune_lightgbm(X_sub, y_noisy, X_val, y_val)  ← re-tune per condition
                  Phase 5b: y_val may be noisy or clean (sub-experiment)
                  → (fitted_model, best_params)
                  → evaluate on clean test
```

---

## Common Tasks

### Tune LightGBM for one endpoint

```python
from src.tuning import tune_lightgbm, save_params

X_train_tune, X_val, y_train_tune, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
model, params = tune_lightgbm(X_train_tune, y_train_tune, X_val, y_val, n_iter=50, random_state=42)
save_params(params, 'models/tuned_params/HLM_lgbm.json')
metrics = evaluate_model(model, X_test, y_test)  # model already refitted on train+val
```

### Re-tune under experimental condition (Phase 4–6, tuned arm)

```python
from src.tuning import tune_lightgbm

# Re-tune on noisy/subsampled data with a fixed val set
# Phase 5b: pass y_val_noisy instead of y_val for the noisy-val arm
X_sub_tune, X_val, y_sub_tune, y_val = train_test_split(X_sub, y_noisy, test_size=0.2, random_state=42)
model, params = tune_lightgbm(X_sub_tune, y_sub_tune, X_val, y_val, n_iter=50, random_state=42)
metrics = evaluate_model(model, X_test_clean, y_test_clean)
```

---

## Implementation Notes

### Two-arm experiment design

**Issue**: Need to compare baseline (default hyperparameters) vs tuned models under varying data quantity and noise.

**Solution**: Phase 3 tunes on clean full data as a reference. Phases 4–6 run two arms per condition: (1) baseline arm with default hyperparameters, (2) tuned arm that re-tunes via `RandomizedSearchCV` on each subsample/noisy dataset. This shows whether tuning buys resilience under degraded conditions. A separate sub-experiment (Phase 5b) compares noisy vs clean validation sets during tuning.

**Location**: `src/tuning/tuning.py`

### RandomizedSearchCV over GridSearchCV

**Issue**: GridSearchCV over 6 hyperparameters scales exponentially. Prohibitive for a 6-week project.

**Solution**: RandomizedSearchCV with `n_iter=50` gives good coverage at fixed cost. Reproducible via `random_state=42`.

**Location**: `src/tuning/tuning.py`

### MPNN2: early stopping, not grid search

**Issue**: ChemProp training takes ~10min per run. Grid search (8 combos × 6 endpoints) is prohibitive.

**Solution**: Fixed architecture (`hidden_size=300, depth=3`), generous `--epochs 50`, ChemProp's built-in early stopping on internal validation split. Standard approach in ChemProp literature.

**Location**: notebook section 3.2

---

**Last Updated**: 2026-07-20 | **Status**: Active | **Maintainer**: Zarif

# Models — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Provide a fixed set of five sklearn-compatible baseline regressors and a uniform evaluation function so all ADME endpoint experiments report comparable R², RMSE, and MSE.

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless)* | — | All functions are factories or pure computations; no mutable state is held |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `get_baseline_models` | `() → dict[str, estimator]` | Returns a fresh dict of five unfitted sklearn-compatible regressors keyed by display name |
| `evaluate_model` | `(model, X_test, y_test) → dict[str, float]` | Calls `model.predict(X_test)`, computes and returns `{"R2": float, "RMSE": float, "MSE": float}` |

### Invariants

- `get_baseline_models()` must always return exactly these five keys: `"LinearRegression"`, `"BayesianRidge"`, `"RandomForest"`, `"XGBoost"`, `"LightGBM"`
- All returned estimators must implement `.fit(X, y)` and `.predict(X)` (sklearn interface)
- `evaluate_model()` must always return all three keys: `"R2"`, `"RMSE"`, `"MSE"`
- `R2` ∈ (−∞, 1.0]; `RMSE` ≥ 0; `MSE` ≥ 0
- `evaluate_model()` does not fit the model — caller is responsible for fitting before passing

---

## Architecture

```
get_baseline_models()
    │
    └─► {"LinearRegression": LinearRegression(),
         "BayesianRidge":    BayesianRidge(),
         "RandomForest":     RandomForestRegressor(n_estimators=100, random_state=42),
         "XGBoost":          XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
         "LightGBM":         LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)}
              │
              ▼  caller: model.fit(X_train, y_train)
              │
evaluate_model(model, X_test, y_test)
    │
    └─► y_pred = model.predict(X_test)
        → {"R2": r2_score, "RMSE": sqrt(MSE), "MSE": mean_squared_error}
```

---

## Common Tasks

### Train and evaluate all 5 models on one endpoint

```python
from src.models import get_baseline_models, evaluate_model

models = get_baseline_models()
results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    results[name] = evaluate_model(model, X_test, y_test)
```

### Build results DataFrame across all endpoints

```python
import pandas as pd
rows = []
for endpoint, (X_train, X_test, y_train, y_test) in splits.items():
    for name, model in get_baseline_models().items():
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        rows.append({"endpoint": endpoint, "model": name, **metrics})
results_df = pd.DataFrame(rows)
```

---

## Implementation Notes

### Fixed model set, no registry

**Issue**: A plugin registry pattern would add complexity with no benefit for a 6-week project with exactly 5 fixed models.

**Solution**: `get_baseline_models()` returns a hardcoded dict. If models change, edit the function directly.

**Location**: `src/models/models.py`

### BayesianRidge as Bayesian baseline

**Issue**: PrO posteriors (Fong & Holmes, 2025) are theoretically relevant but too costly to implement. See ADR-001 in DECISIONS.md.

**Solution**: `BayesianRidge` (sklearn) provides a Bayesian comparison point at zero implementation cost.

**Location**: `src/models/models.py`

---

**Last Updated**: 2026-07-13 | **Status**: Active | **Maintainer**: Zarif

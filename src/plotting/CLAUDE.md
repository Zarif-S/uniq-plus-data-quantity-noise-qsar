# Plotting - UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Produce reusable EDA and results figures as self-contained matplotlib Figure objects.

### State

Stateless — all functions accept DataFrames and return Figure objects; no module-level state is held.

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `endpoint_distributions` | `(df, endpoint_cols, figsize=(14, 8)) → Figure` | Histogram + KDE grid for each endpoint column; grid dimensions computed from number of columns |
| `pred_vs_actual_grid` | `(preds_dict, title="", figsize=None) → Figure` | Scatter grid of predicted vs actual per model; `preds_dict` is `{model_name: (y_test, y_pred)}`; annotates each panel with R² |

### Invariants

- Returns exactly one `matplotlib.figure.Figure` — no side effects, no stdout output
- Input DataFrame is never modified
- NaN values are silently dropped per column before plotting (see NaN asymmetry note below)
- Grid is always `n_cols = min(3, n)`, `n_rows = ceil(n / n_cols)` — never hardcoded
- KDE is skipped if a column has fewer than 2 non-NaN values or zero variance
- Unused subplot panels are hidden, never left as empty visible axes

---

## Architecture

```
DataFrame + endpoint_cols
        │
        ▼
endpoint_distributions()
        │
        ├── compute grid: n_cols = min(3, n), n_rows = ceil(n / n_cols)
        │
        ├── per column: dropna → histogram → KDE (if variance > 0)
        │
        └──→ matplotlib Figure
```

---

## Common Tasks

### Plot endpoint distributions for EDA

Run `missing_value_report` first to understand what the silent NaN drop will exclude:

```python
from src.eda import missing_value_report
from src.plotting import endpoint_distributions

endpoint_cols = ["HLM", "RLM", "MDR1", "Sol", "PPB_h", "PPB_r"]

# Check NaN counts before plotting
print(missing_value_report(df, endpoint_cols))

# Plot distributions of valid data
fig = endpoint_distributions(df, endpoint_cols)
fig.savefig("figures/endpoint_distributions.png", dpi=150, bbox_inches="tight")
```

---

## Implementation Notes

### NaN asymmetry — plotting is the only module that tolerates NaN

**Issue**: `features` raises `ValueError` on invalid/NaN input; `plotting` silently drops NaN rows. This asymmetry is intentional, not an oversight.

**Solution**: For featurisation, a NaN row corrupts the entire feature matrix passed to a model — strict validation is correct. For visualisation, plotting the distribution of whatever valid data exists is still meaningful and is the expected EDA behaviour. Silently dropping NaN keeps the function simple and noise-free. The caller should run `missing_value_report` first if they need to know exactly how many rows are excluded.

**Location**: `src/plotting/plotting.py:28`

### Flexible grid — computed from number of endpoints

**Issue**: The original implementation hardcoded a 2×3 grid, which would crash or produce wrong layouts for datasets with more or fewer than 6 endpoints (e.g. PDE10A has 1 endpoint).

**Solution**: Grid dimensions are computed as `n_cols = min(3, n)`, `n_rows = ceil(n / n_cols)`. Works for any number of endpoints. `squeeze=False` on `plt.subplots` ensures `axes` is always a 2D array regardless of grid size.

**Location**: `src/plotting/plotting.py:16–19`

---

**Last Updated**: 2026-07-10 | **Status**: Active | **Maintainer**: Zarif

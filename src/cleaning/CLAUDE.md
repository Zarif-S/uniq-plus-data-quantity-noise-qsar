# Cleaning — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Filter per-endpoint missing values and detect IQR outliers so each baseline model trains on clean, complete rows for its specific target.

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless)* | — | All functions are pure transforms on DataFrames; no mutable state is held |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `filter_endpoint` | `(df, endpoint_col) → DataFrame` | Drops rows where `endpoint_col` is NaN; returns filtered DataFrame with all other columns intact |
| `flag_iqr_outliers` | `(df, endpoint_col, k=1.5) → Series[bool]` | Computes Q1/Q3 bounds; returns boolean mask (True = outlier) for rows outside [Q1 − k·IQR, Q3 + k·IQR] |

### Invariants

- `filter_endpoint` must return only rows where `endpoint_col` is non-NaN — no NaN values may remain in the target column of the output
- `flag_iqr_outliers` must never modify `df` in place — the source DataFrame is unchanged
- `flag_iqr_outliers` raises `ValueError` if `endpoint_col` contains NaN — `filter_endpoint` must be called first
- The outlier mask returned by `flag_iqr_outliers` must have the same index as `df`
- IQR multiplier `k` defaults to 1.5; callers may override but 1.5 is the project standard
- Flagged outliers are never removed — this module only detects, never filters on outlier status

---

## Architecture

```
Raw DataFrame (3521 rows, 6 endpoints)
          │
          ▼ filter_endpoint(df, "LOG HLM_CLint")
Filtered DataFrame (N_hlm rows, NaN-free for HLM)
          │
          ├──► flag_iqr_outliers(df_hlm, "LOG HLM_CLint")
          │         → bool mask  (logged, not applied)
          │
          └──► passed to src/features for fingerprinting
```

---

## Common Tasks

### Check how many rows each endpoint retains

```python
from src.cleaning import filter_endpoint
for col in ENDPOINT_COLS:
    df_ep = filter_endpoint(df, col)
    print(f"{col}: {len(df_ep)} rows")
```

### Flag IQR outliers for an endpoint

```python
from src.cleaning import flag_iqr_outliers
mask = flag_iqr_outliers(df_hlm, "LOG HLM_CLint")
print(f"Outliers flagged: {mask.sum()}")
```

---

## Implementation Notes

### Per-endpoint filtering over complete-case

**Issue**: Complete-case filtering (drop any row missing any endpoint) retains only ~180 rows (5% of data) because PPB_HUMAN and PPB_RAT are 94–95% missing.

**Solution**: Train each model independently on its own non-NaN subset. PPB models get ~170–190 samples; HLM/RLM models get ~3000+.

**Location**: `src/cleaning/cleaning.py`

### IQR flag-only policy

**Issue**: Outliers in SOLUBILITY (left-skewed, skewness = −1.64) could distort 3σ detection. IQR is more robust for non-normal distributions.

**Solution**: Use 1.5×IQR rule for detection. Flagged rows are logged but never removed — this is a noise-study project where extreme values carry scientific meaning.

**Location**: `src/cleaning/cleaning.py`

---

**Last Updated**: 2026-07-13 | **Status**: Active | **Maintainer**: Zarif

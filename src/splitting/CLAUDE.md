# Splitting — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Expose pre-defined train/test splits from PDE10A CSV split columns so each of the 7 split strategies can be applied consistently without reimplementing filtering logic per notebook.

### State

| Field | Type | Description |
|-------|------|-------------|
| `SPLIT_COLS` | `List[str]` | The 7 split column names present in the PDE10A CSV (constants; see below) |
| *(otherwise stateless)* | — | All functions are pure transforms on DataFrames; no mutable state is held |

**`SPLIT_COLS`** (in dataset order):
```python
SPLIT_COLS = [
    "aminohetaryl_c1_amide_split",
    "aryl_c1_amide_c2_hetaryl_split",
    "temporal_2012_split",
    "c1_hetaryl_alkyl_c2_hetaryl_split",
    "temporal_2013_split",
    "temporal_2011_split",
    "random_split",
]
```

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `get_split` | `(df: DataFrame, split_col: str) → (DataFrame, DataFrame)` | Filters `df` on `split_col`; returns `(train_df, test_df)`; `val` rows are silently discarded |
| `list_split_cols` | `(df: DataFrame) → List[str]` | Returns the subset of `SPLIT_COLS` present in `df.columns` |

### Invariants

- `split_col` must be a column in `df`; raises `ValueError` if not
- `train_df` and `test_df` are disjoint — no row index appears in both
- `val` rows are never returned; only rows where `split_col == "train"` or `split_col == "test"` are included
- Neither `train_df` nor `test_df` may be empty after filtering; raises `ValueError` if either is
- `get_split` never mutates `df` — the source DataFrame is unchanged

---

## Architecture

```
PDE10A DataFrame (raw, with 7 split columns)
          │
          ▼  list_split_cols(df)
     SPLIT_COLS (7 column names)
          │
          │  for split_col in SPLIT_COLS:
          ▼
     get_split(df, split_col)
          │
          ├── filter split_col == "train"  →  train_df
          ├── filter split_col == "test"   →  test_df
          └── filter split_col == "val"    →  (discarded)
```

---

## Common Tasks

### Get a single split for training

```python
from src.splitting import get_split

train_df, test_df = get_split(df, "random_split")
# train_df and test_df are ready for featurization
```

### Iterate over all 7 splits for cross-split comparison

```python
from src.splitting import get_split, SPLIT_COLS

results = {}
for split_col in SPLIT_COLS:
    train_df, test_df = get_split(df, split_col)
    # featurize, train, evaluate ...
    results[split_col] = metrics
```

---

## Implementation Notes

### Pre-defined splits over random generation

**Issue**: PDE10A splits encode meaningful scientific distinctions (temporal holdout, chemotype generalisation, random) that cannot be reproduced by sklearn's `train_test_split`. Generating splits randomly would discard this structure.

**Solution**: Splits are read directly from the CSV columns. This module provides a thin, validated wrapper around column filtering — it does not generate splits. See [SYNC-007](../../SYNCHRONIZATIONS.md#sync-007) for how the Cleaning→Splitting handoff is formalised.

**Location**: `src/splitting/splitting.py`

### Val rows ignored by design

**Issue**: Each split column has three labels — `train`, `test`, `val`. For Phase 2 baselines, there is no hyperparameter tuning step that needs a validation set, and treating `val` differently across split types (e.g. temporal vs. random) would introduce inconsistency in the cross-split comparison.

**Solution**: `get_split` discards `val` rows unconditionally. This keeps train/test semantics consistent across all 7 splits. Val rows remain in the raw DataFrame if needed for future use (e.g. as a second evaluation horizon in Phase 3 learning curves).

**Location**: `src/splitting/splitting.py`

---

**Last Updated**: 2026-07-13 | **Status**: Active | **Maintainer**: Zarif

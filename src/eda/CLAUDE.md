# EDA — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Validate and profile raw molecular datasets so cleaning and modelling decisions are grounded in observed data quality.

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless)* | — | All functions operate on DataFrames passed in and return new objects; no module-level state is held |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `smiles_validity_report` | `(df, smiles_col="SMILES") → dict` | Returns `{valid_count, invalid_count, invalid_indices}` for all SMILES in the column |
| `missing_value_report` | `(df, endpoint_cols) → DataFrame` | Returns DataFrame of `n_missing` and `pct_missing` per endpoint column |

### Invariants

- Input DataFrame is never modified — both functions are pure reads
- Applied to raw data only — EDA must run before any cleaning or filtering
- `smiles_validity_report` counts and indexes invalid SMILES; it never silently skips them
- `missing_value_report` returns one row per endpoint; index matches `endpoint_cols` order
- Neither function drops, fills, or transforms any data — outputs are reporting objects only

---

## Architecture

```
raw CSV → DataFrame
              │
              ├──→ smiles_validity_report(df)  → {valid_count, invalid_count, invalid_indices}
              │
              └──→ missing_value_report(df, endpoint_cols)
                        → DataFrame (n_missing, pct_missing per endpoint)
```

---

## Common Tasks

### Run SMILES validity check

```python
from src.eda import smiles_validity_report

report = smiles_validity_report(df, smiles_col="SMILES")
print(report["invalid_count"], "invalid SMILES at indices:", report["invalid_indices"])
```

### Run missing value report

```python
from src.eda import missing_value_report

report = missing_value_report(df, ENDPOINT_COLS)
display(report)  # shows n_missing and pct_missing per endpoint
```

---

**Last Updated**: 2026-07-13 | **Status**: Active | **Maintainer**: Zarif

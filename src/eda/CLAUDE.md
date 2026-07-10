# src/eda — EDA Module

**Purpose**: Validate and inspect raw molecular datasets before any cleaning or modelling decisions.

**State**: Stateless — operates on DataFrames passed in, returns new objects, never mutates input.

---

## Public API

| Function | Signature | Returns |
|----------|-----------|---------|
| `smiles_validity_report` | `(df, smiles_col="SMILES") → dict` | `{valid_count, invalid_count, invalid_indices}` |
| `missing_value_report` | `(df, endpoint_cols) → DataFrame` | DataFrame with `n_missing`, `pct_missing` per endpoint column |

---

## Invariants

- Input DataFrame is never modified
- Applied to raw data only (before any cleaning)
- Returns are reporting objects only — no rows are dropped or filtered
- Invalid SMILES are counted and indexed, not silently skipped

---

## Architecture

```
raw CSV → DataFrame → smiles_validity_report  → report dict
                    → missing_value_report    → report DataFrame
```

---

## Common Tasks

**Run SMILES validity check:**
```python
from src.eda import smiles_validity_report
report = smiles_validity_report(df, smiles_col="SMILES")
print(report["invalid_count"], "invalid SMILES at indices:", report["invalid_indices"])
```

**Run missing value report:**
```python
from src.eda import missing_value_report
endpoint_cols = ["HLM", "RLM", "MDR1", "Sol", "PPB_h", "PPB_r"]
report = missing_value_report(df, endpoint_cols)
```

---

## Known Issues

None. Both functions are simple and tested implicitly in the notebook.

---

## Navigation

- Root CLAUDE.md: [../../CLAUDE.md](../../CLAUDE.md)
- ROADMAP: [../../ROADMAP.md](../../ROADMAP.md)
- PROJECT_PLAN: [../../PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- SYNCHRONIZATIONS: [../../SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- src overview: [../CLAUDE.md](../CLAUDE.md)

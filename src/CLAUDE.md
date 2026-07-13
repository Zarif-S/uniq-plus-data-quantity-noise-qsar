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

---

## Pipeline

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
[plotting] — visualise distributions, predicted vs actual
```

---

## Cross-Cutting Invariants

- All modules accept molecular data via a pandas DataFrame (SMILES as a column) or a list of SMILES strings
- No module modifies raw data — inputs are never mutated
- All functions are stateless: same inputs always produce same outputs
- `src/__init__.py` does NOT exist (namespace packages; adding one would break imports)

---

## Navigation

- Root CLAUDE.md: [../CLAUDE.md](../CLAUDE.md)

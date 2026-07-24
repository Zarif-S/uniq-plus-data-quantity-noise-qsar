# Features - UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Convert pre-validated SMILES strings into numerical feature matrices ready for ML model training.

### State

Stateless — all functions operate on inputs passed in and return new objects; no module-level state is held.

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `morgan_fingerprints` | `(smiles_list, radius=2, n_bits=1024) → np.ndarray` | Returns (N, n_bits) int array of FCFP4 fingerprints (always useFeatures=True) |
| `rdkit_descriptors` | `(smiles_list) → pd.DataFrame` | Returns DataFrame of 6 RDKit 2D descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds) |

### Invariants

- Input list is never modified
- Output always has exactly `len(smiles_list)` rows — no rows are dropped
- Invalid SMILES raises `ValueError` immediately — callers must pre-validate with `smiles_validity_report` before calling either function
- `morgan_fingerprints` always returns dtype int with shape `(N, n_bits)`
- `rdkit_descriptors` always returns exactly 6 columns in order: MW, LogP, TPSA, HBD, HBA, RotBonds
- Morgan FP defaults (radius=2, n_bits=1024, useFeatures=True fixed) are fixed project constants matching Fang et al. (2023) FCFP4 setup — do not change without a documented reason
- Neither function standardizes input mols — both parse SMILES directly via `Chem.MolFromSmiles`. Caller must pass already-standardized SMILES (via `src.preprocessing.standardize`) upstream if standardization matters; there is no internal safeguard against unstandardized input

---

## Architecture

```
pre-validated SMILES list
        │
        ├──→ morgan_fingerprints(smiles_list) ──→ np.ndarray (N, 1024)   [tree models: RF, XGBoost, LightGBM]
        │
        └──→ rdkit_descriptors(smiles_list)   ──→ pd.DataFrame (N, 6)    [interpretable baselines / EDA]
```

---

## Common Tasks

### Compute Morgan fingerprints for a dataset

Pre-validate SMILES first, then featurise:

```python
from src.eda import smiles_validity_report
from src.features import morgan_fingerprints

report = smiles_validity_report(df, smiles_col="SMILES")
assert report["invalid_count"] == 0, f"Fix {report['invalid_count']} invalid SMILES first"

X = morgan_fingerprints(df["SMILES"].tolist())  # shape (N, 1024)
```

### Compute RDKit 2D descriptors

```python
from src.features import rdkit_descriptors

desc = rdkit_descriptors(df["SMILES"].tolist())
# columns: MW, LogP, TPSA, HBD, HBA, RotBonds
```

---

## Implementation Notes

### Raise on invalid SMILES — no silent fill

**Issue**: The original implementation silently substituted zero vectors (morgan_fingerprints) or NaN rows (rdkit_descriptors) for invalid SMILES. This inconsistency could mask data quality problems and produce subtly wrong feature matrices without any warning.

**Solution**: Both functions now raise `ValueError` on any invalid SMILES. The expected workflow is: run `smiles_validity_report` → clean/remove invalid rows → then featurise. This makes data quality problems immediately visible and keeps the two functions consistent.

**Location**: `src/features/features.py`

### Morgan FP defaults are fixed project constants

**Issue**: `radius` and `n_bits` are exposed as parameters, but varying them mid-project would confound the data quantity and noise experiments (the core research question is about dataset size and noise, not featurizer choice).

**Solution**: Defaults (radius=2, n_bits=1024, use_features=True) match the Fang et al. (2023) FCFP4 setup. Documented as fixed project constants. Only change with a clear justification and a dedicated experiment branch.

**Location**: `src/features/features.py:12`

---

**Last Updated**: 2026-07-10 | **Status**: Active | **Maintainer**: Zarif

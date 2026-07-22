# Noise — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Inject controlled label noise into training target vectors to simulate real-world assay imperfections (intra-assay variability, inter-assay bias, annotation errors) for the noise-robustness experiments.

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless)* | — | All functions accept a target array and return a new noisy array; no module-level state is held |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `add_gaussian_noise` | `(y, sigma_frac, random_state=None) → ndarray` | Intra-assay noise: adds N(0, sigma_frac × std(y)) independently to each label |
| `add_systematic_bias` | `(y, bias_frac, affected_frac=0.5, random_state=None) → ndarray` | Inter-assay noise: applies a constant bias of `bias_frac × std(y)` to a random fraction of labels |
| `add_gross_errors` | `(y, error_frac, random_state=None) → ndarray` | Annotation errors: replaces `error_frac` of labels with uniform random values drawn from [y.min(), y.max()] |

### Theoretical Ceiling (Gaussian only)

For Gaussian noise, `NoiseEstimator` (Corradi & van Hilten, ChemRxiv 2024; doi:10.26434/chemrxiv-2024-z0pz7) computes the bootstrapped R² ceiling: the best score a perfect clean-label predictor achieves when *evaluated against noisy labels*. Analytically: **R² = 1 − σ²/Var(y)**. Used in `03_adme_experiments.ipynb` to overlay a reference line on Gaussian degradation plots. **Not applicable to gross errors or systematic bias** — library only supports Gaussian noise. Requires input as `pd.Series` (not numpy array).

---

### Invariants

- Input `y` is never modified — all functions return a new array (pure functions)
- All functions are reproducible when `random_state` is set
- Noise scale is always relative to `std(y)` — scale-invariant across endpoints
- Gross errors stay within the observed range `[y.min(), y.max()]` — no out-of-distribution outliers
- These functions are applied to `y_train` only — test labels are never corrupted

---

## Architecture

```
y_train (clean)
      │
      ▼
[noise fn]  ← sigma_frac / bias_frac / error_frac parameter
      │
      ▼
y_noisy
      │
      ▼
model training loop  → fitted model
      │
      ▼
evaluate on y_test (always clean)
```

---

## Common Tasks

### Add Gaussian noise (intra-assay)

```python
from src.noise import add_gaussian_noise

y_noisy = add_gaussian_noise(y_train, sigma_frac=0.1, random_state=42)
# adds noise ~ N(0, 0.1 * std(y_train)) to each label
```

### Add systematic bias (inter-assay)

```python
from src.noise import add_systematic_bias

y_noisy = add_systematic_bias(y_train, bias_frac=0.2, affected_frac=0.5, random_state=42)
# shifts 50% of labels by +0.2 * std(y_train)
```

### Add gross errors (annotation errors)

```python
from src.noise import add_gross_errors

y_noisy = add_gross_errors(y_train, error_frac=0.05, random_state=42)
# replaces 5% of labels with random values in [y.min(), y.max()]
```

---

**Last Updated**: 2026-07-20 | **Status**: Active | **Maintainer**: Zarif

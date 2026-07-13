# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 📍 Breadcrumbs

- **Looking for strategic vision?** → [ROADMAP.md](ROADMAP.md)
- **Looking for current sprint work?** → [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Looking for implementation details?** → [CLAUDE.md](CLAUDE.md)

---

## [Unreleased]

### Added (2026-07-13 — Phase 1 completion)
- `src/cleaning/` subpackage: `filter_endpoint` (per-endpoint NaN filtering) and `flag_iqr_outliers` (1.5×IQR outlier detection, flag-only)
- `src/models/` subpackage: `get_baseline_models` (5-model factory) and `evaluate_model` (R², RMSE)
- `src/plotting.pred_vs_actual_grid`: scatter grid of predicted vs actual per model, annotated with R²
- `src/cleaning/CLAUDE.md`, `src/models/CLAUDE.md` — concept specifications for new modules
- `tests/test_cleaning.py` (6 tests), `tests/test_models.py` (4 tests) — all 18 tests passing
- `notebooks/01_adme_eda_baseline.ipynb` Part 1B: IQR outlier detection (§1.11), per-endpoint row count table (§1.12)
- `notebooks/01_adme_eda_baseline.ipynb` Part 2: featurization (§2.1), train/test split (§2.2), model training (§2.3), results tables (§2.4), predicted vs actual plots (§2.5)
- `DECISIONS.md` ADR-002: per-endpoint filtering over imputation — rationale and implications documented
- `ipykernel` added as dev dependency; venv registered as "UNIQ+ (Python 3.10)" Jupyter kernel

### Changed (2026-07-13)
- `src/CLAUDE.md`: added `cleaning` and `models` rows to module table; updated pipeline diagram
- `SYNCHRONIZATIONS.md`: SYNC-002 resolved (per-endpoint filtering decided); SYNC-005 model names updated to match actual `get_baseline_models()` keys
- `src/cleaning.flag_iqr_outliers`: raises `ValueError` if endpoint column contains NaN — `filter_endpoint` must be called first
- Root `CLAUDE.md` navigation updated with `src/cleaning/CLAUDE.md` and `src/models/CLAUDE.md` entries
- `PROJECT_PLAN.md`: Phase 1 marked complete; Phase 2 set as current focus

### Added (2026-07-10 — Phase 1 EDA)
- `src/eda/` subpackage: `smiles_validity_report` and `missing_value_report` utilities
- `src/features/` subpackage: `morgan_fingerprints` (ECFP4, radius=2, 2048-bit) and `rdkit_descriptors` (MW, LogP, TPSA, HBD, HBA, RotBonds)
- `src/plotting/` subpackage: `endpoint_distributions` — histogram + KDE grid, flexible layout
- `src/eda/CLAUDE.md`, `src/features/CLAUDE.md`, `src/plotting/CLAUDE.md` — concept specifications
- `src/CLAUDE.md` — src module index with pipeline diagram and cross-cutting invariants
- `tests/test_eda.py`, `tests/test_features.py`: unit tests
- `notebooks/01_adme_eda_baseline.ipynb`: ADME EDA notebook (Sections 1.1–1.10)

---

**Last Updated**: 2026-07-13

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

### Added
- `src/eda/` subpackage: `smiles_validity_report` and `missing_value_report` utilities
- `src/features/` subpackage: `morgan_fingerprints` (ECFP4, radius=2, 2048-bit) and `rdkit_descriptors` (MW, LogP, TPSA, HBD, HBA, RotBonds)
- `src/plotting/` subpackage: endpoint distribution histograms with KDE overlay, flexible grid layout
- `src/eda/CLAUDE.md`, `src/features/CLAUDE.md`, `src/plotting/CLAUDE.md` — concept specifications for all three src modules
- `src/CLAUDE.md` — src module index with pipeline diagram and cross-cutting invariants
- `tests/test_eda.py`, `tests/test_features.py`: unit tests (7/7 passing)
- `notebooks/01_adme_eda_baseline.ipynb`: ADME EDA notebook (Sections 1.1–1.10); runs top-to-bottom from fresh kernel

### Changed
- `src/features`: `morgan_fingerprints` and `rdkit_descriptors` now raise `ValueError` on invalid SMILES (previously silently filled with zeros/NaN); callers must pre-validate with `smiles_validity_report` first
- `src/plotting`: grid layout now computed dynamically from number of endpoints (`n_cols = min(3, n)`, `n_rows = ceil(n / n_cols)`) — no longer hardcoded 2×3
- `ROADMAP.md`: featurization section updated from TBD to ECFP4 confirmed
- `PROJECT_PLAN.md`: featurization decision resolved; removed from Active Decisions Pending
- Root `CLAUDE.md` navigation table updated to point to `src/CLAUDE.md`
- `notebooks/01_adme_eda_baseline.ipynb`: SMILES validity assertion added before `rdkit_descriptors` call in section 1.9

---

**Last Updated**: 2026-07-10

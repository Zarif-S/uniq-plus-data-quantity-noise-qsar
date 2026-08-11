# Feature Selection — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)
- **Full walkthrough + design rationale** → [notebooks/01.8_feature_selection.ipynb](../../notebooks/01.8_feature_selection.ipynb)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Select a global (endpoint-agnostic) subset of the paper's 50 rdmoldes descriptors
(316 expanded features) for the RF/LightGBM/FCNN data-quantity + noise study, operating at the
*descriptor* level (44 single-feature scalars + 6 multi-feature vector descriptors like
`AUTOCORR2D` → 192 features) rather than the individual expanded-feature level.

### State

Stateless — all functions operate on inputs passed in and return new objects; no module-level
state is held.

### Actions

| Action | Signature | Description |
|--------|-----------|--------------|
| `rdmoldes_descriptor_map` | `() → {descriptor_name: [feature indices]}` | Maps the 50 named descriptors to their column ranges in `rdmoldes()`'s 316-feature output |
| `drop_constant_descriptors` | `(X, descriptor_map, threshold=1e-8) → (kept_map, dropped_names)` | Drops a descriptor only if *every* feature in it has ~zero variance |
| `descriptor_component_matrix` | `(X, descriptor_map, n_components=5, random_state=42) → {name: (n_rows, k) array}` | Top-k PCA per descriptor (z-scored first); k=1 for scalar descriptors |
| `descriptor_pc1_matrix` | `(component_map) → pd.DataFrame` | First component only, one column per descriptor — used for VIF |
| `mutual_info_per_descriptor` | `(component_map, y_by_endpoint, random_state=42) → (mi_max, mi_table)` | MI(descriptor's best component, endpoint), max'd across endpoints |
| `correlation_prune` | `(component_map, mi_scores, threshold=0.9) → (kept_names, dropped_records)` | Drops one of each near-duplicate pair (canonical correlation between top-component sets), MI tiebreak |
| `vif_prune` | `(pc1_df, mi_scores, threshold=5.0, tie_margin=0.05) → (kept_names, trace)` | Iteratively drops the highest-VIF descriptor (multicollinearity vs. all others), MI tiebreak on near-ties |
| `vif_mi_table` | `(pc1_df, mi_scores) → pd.DataFrame` | Diagnostic: VIF + MI + both ranks for every descriptor at once, before any elimination |
| `evaluate_descriptor_set` | `(X_by_endpoint, y_by_endpoint, descriptor_map, descriptors, cv=5, random_state=42) → dict` | Mean + per-endpoint CV R² for a descriptor subset's real features — used to audit each pruning stage's actual cost |
| `run_descriptor_rfe` | `(X_by_endpoint, y_by_endpoint, descriptor_map, min_descriptors=5, cv=5, random_state=42) → trace` | LightGBM recursive descriptor elimination; returns a full per-step CV-score trace for the caller to inspect and pick a cutoff — does not auto-decide a final set |

### Invariants

- All selection decisions are made at the **descriptor** level (50 named things), never by
  splitting a multi-feature descriptor across its own features
- `correlation_prune` and `mutual_info_per_descriptor` operate on each descriptor's top-k PCA
  components (via `descriptor_component_matrix`), not a single PC1 — a large descriptor like
  `AUTOCORR2D` (192 features) is judged on more than one coincidental axis
- `vif_prune`/`descriptor_pc1_matrix` are the one deliberate exception: VIF is a
  single-variable-vs-the-rest statistic and is kept PC1-only rather than generalised
- Every relevance/redundancy tiebreak uses **max MI across the 4 endpoints** — "keep a descriptor
  if it's useful for *any* endpoint," per the project's per-endpoint modelling decision
- `run_descriptor_rfe` never silently picks a final descriptor count — it returns a trace and
  leaves the cutoff decision to whoever calls it, specifically so an aggressive elimination isn't
  trusted without a human looking at the CV-score-vs-descriptors curve
- The current `selected_descriptors.json` selection is global across all 4 endpoints, not
  per-endpoint — only revisit with a per-endpoint re-selection if one endpoint's downstream model
  performance is significantly worse than the others (SOL is already the weakest at the current
  5-descriptor cutoff, R²=0.272 — the natural first candidate to check)
- No function mutates its inputs; all are pure given the same arguments

---

## Architecture

```
rdmoldes() output (N, 316)
        │
        ▼
[1] drop_constant_descriptors        -- degenerate descriptors out (data-only, no target)
        │
        ▼
[2] descriptor_component_matrix      -- top-k PCA per descriptor (MI + correlation-pruning only)
        │
        ▼
[3] mutual_info_per_descriptor       -- MI(descriptor, endpoint), max across endpoints
        │
        ▼
[4] correlation_prune (CCA)          -- near-duplicate descriptors out, MI tiebreak
        │
        ▼
[5] vif_prune (+ vif_mi_table)       -- multicollinear descriptors out, MI tiebreak
        │
        ▼
[6] run_descriptor_rfe               -- LightGBM elimination + CV-score trace
        │
        ▼
human inspects the trace, picks a cutoff (see notebooks/01.8_feature_selection.ipynb §6)
        │
        ▼
data/processed/selected_descriptors.json
```

---

## Common Tasks

### Reproduce the selection end-to-end

Run `notebooks/01.8_feature_selection.ipynb` top-to-bottom (~5 min, dominated by section 5's
RFE loop). It loads `data/processed/section3_feat.pkl` (already-featurised ADME data from
`01.5`), runs the full pipeline, and writes `data/processed/selected_descriptors.json`.

### Audit R² at any descriptor subset

```python
from src.feature_selection import evaluate_descriptor_set

r2 = evaluate_descriptor_set(X_by_endpoint, y_by_endpoint, descriptor_map, some_descriptor_list)
print(r2['mean'])  # mean CV R^2 across the 4 endpoints
```

### `selected_descriptors.json` schema

```
selected_descriptors                      list[str]  the 5 final descriptor names
selected_features                         list[int]  corresponding column indices into rdmoldes()'s 316-feature output
cv_score_mean                             float      mean CV R^2 across 4 endpoints at the final cutoff
cv_score_by_endpoint                      dict       per-endpoint CV R^2 at the final cutoff
baseline_cv_score_mean                    float      CV R^2 with all non-constant descriptors (no pruning)
post_cca_correlation_prune_cv_score_mean  float      CV R^2 after correlation-prune
post_vif_prune_cv_score_mean              float      CV R^2 after VIF-prune
dropped_constant                          list[str]  constant-filter drops
dropped_correlation                       list[dict] correlation-prune drops: {dropped, kept_instead, canonical_corr}
dropped_vif                               list[dict] VIF-prune drops: {dropped, vif, mi, remaining}
```

---

## Implementation Notes

### Deduplicate molecules before variance/correlation/VIF

**Issue**: Many compounds are tested across more than one of the 4 modelling endpoints. Naively
row-stacking all 4 endpoints' `rdkit` matrices for the redundancy analysis (steps 1–5, which only
look at `X`, never `y`) would count those molecules 2–4x, giving them outsized influence on what
"typical" descriptor redundancy looks like.

**Solution**: Steps 1–5 pool only the **unique molecules** (deduplicated by canonical SMILES).
Verified this mattered: with deduplication, correlation-prune's R² cost dropped from −0.023 to
−0.014 relative to baseline — duplicate-weighted correlation estimates were genuinely making
descriptors look more redundant than they are. Step 6 (RFE) and the MI step still use each
endpoint's own full (non-deduplicated) rows against its own target, since that's real modelling
data, not a redundancy-estimation concern.

**Location**: `notebooks/01.8_feature_selection.ipynb` §1

### Canonical correlation (CCA), not PCA, for the correlation-prune step

**Issue**: PCA (step 2) only describes variation *within* one descriptor. Comparing two
descriptors' PC1-to-PC1 Pearson correlation privileges each one's single dominant axis and can
miss real redundancy (or falsely flag redundancy) living in later components — especially
consequential for a 192-feature descriptor like `AUTOCORR2D`.

**Solution**: `correlation_prune` uses the first canonical correlation between two descriptors'
full top-k component sets (`_canonical_correlation`, via `sklearn.cross_decomposition.CCA`) — the
standard generalisation of Pearson correlation to two multi-dimensional variable sets.

**Known limitation**: CCA only captures *linear* combinations. A distance-correlation-style
measure (zero iff truly independent, linear or not) would close this gap, at the cost of a new
dependency and O(n²) compute over ~3500 molecules. Not adopted: VIF and the RFE/R² audit
downstream both re-check whatever this step decides against real model performance, so a wrong
call here isn't silently trusted.

**Location**: `src/feature_selection/feature_selection.py::_canonical_correlation`

### VIF can legitimately be `inf`

**Issue**: `vif_prune` occasionally hits a `RuntimeWarning: divide by zero` and reports
`VIF=inf` for a descriptor.

**Explanation, not a bug**: VIF = `1/(1-R²)`. Some of RDKit's ring-count descriptors satisfy
*exact* accounting identities — e.g. `CalcNumAromaticRings = CalcNumAromaticCarbocycles +
CalcNumAromaticHeterocycles` by definition, for every molecule (verified against the actual data,
`np.allclose` = `True`). When both terms of such an identity are still in the candidate pool, the
third is perfectly reconstructable (R²=1 exactly), correctly producing `VIF=inf` — VIF is doing
exactly its job, flagging the most redundant possible descriptor.

**Location**: `src/feature_selection/feature_selection.py::vif_prune`

### The RFE cutoff must be chosen by inspecting the trace, not automated

**Issue**: An early version picked `MIN_BLOCKS=10` and `CV_FOLDS=3` upfront with no data-driven
justification — the trace never searched far enough to find a real elbow, and 3-fold CV was too
noisy to distinguish signal from noise in the step-to-step deltas.

**Solution**: `run_descriptor_rfe` always returns a full trace down to `min_descriptors`; the
notebook explicitly searches down to 1 with `cv=5` and inspects the plotted trace by eye. On the
current data this reveals a first real elbow at 5→4 descriptors (a −0.061 R² drop, roughly 8x any
other single-step change in the 16→5 range) — 5 descriptors is the selected cutoff — and a second,
much larger cliff further down at 3→2 (−0.221). This is a design choice worth re-validating if the
upstream featurization or descriptor pool ever changes: the function itself makes no assumption
about where the elbow will be.

**Location**: `notebooks/01.8_feature_selection.ipynb` §5–6

### `run_descriptor_rfe` was eliminating on split-count, not gain-importance

**Issue**: Every comment/docstring around `run_descriptor_rfe` and the §8 diagnostic described
gain-based importance ("how much a descriptor's splits reduced loss"), but `LGBMRegressor` was
constructed without `importance_type='gain'` — `feature_importances_` therefore returned
scikit-learn's *default*, which for LightGBM is `split`-count (how many times a descriptor was
used to split, regardless of how much each split actually helped). Code and documentation
disagreed about what the elimination step was actually optimizing.

**Found via**: §8's own shadowing diagnostic — `CalcEccentricity` had exactly zero importance in
the full 316-feature model despite being nearly rank-identical (Spearman ρ=1.0) to `CalcNPR2`,
which had real nonzero importance. That's consistent with split-count (a feature never used to
split gets exactly 0, gain or no gain) but was being narrated as a gain-importance finding.

**Fixed**: `importance_type='gain'` set explicitly in `run_descriptor_rfe`'s and the §8
RF/LightGBM-comparison cell's `LGBMRegressor` construction. Re-running the full pipeline changed
the final 5-descriptor selection: `CalcEccentricity`/`CalcPMI3` (both ADR-011 flat-2D-geometry
descriptors) are no longer selected, replaced by `CalcNumAromaticCarbocycles`/`CalcChi3v`. Even on
genuine gain-importance, RFE's own elimination order in the N≤5 tail is still not reliable — see
`notebooks/01.8_feature_selection.ipynb` §9 for why (gain-importance is a marginal measure, which
misprices descriptors that are individually strong but partially correlated with each other).

**Location**: `src/feature_selection/feature_selection.py::run_descriptor_rfe`,
`notebooks/01.8_feature_selection.ipynb` §5, §8, §9

---

## Related

- **ADR-011** (`DECISIONS.md`) — 9 of the 50 rdmoldes descriptors (`CalcPBF`,
  `CalcSpherocityIndex`, `CalcNPR1/2`, `CalcPMI1-3`, `CalcAsphericity`, `CalcEccentricity`,
  `CalcRadiusOfGyration`, `CalcInertialShapeFactor`) are computed on flat 2D coordinates, not real
  3D conformers — inherited from the paper's own methodology, not a bug in this module. Two of
  them (`CalcPBF`, `CalcSpherocityIndex`) are consequently fully degenerate and get dropped by
  `drop_constant_descriptors` on data alone. Two others (`CalcEccentricity`, `CalcPMI3`) survived
  to the final 5-descriptor selection under a buggy RFE run (see the split-vs-gain-importance note
  above); after that fix, none of the 9 affected descriptors are in the current selection. See
  ADR-011's *Second correction* and the real-conformer diagnostic result (`notebooks/01.8_feature_selection.ipynb`
  §7, `data/processed/adr011_3d_diagnostic.json`).

---

**Last Updated**: 2026-08-10 | **Status**: Active | **Maintainer**: Zarif

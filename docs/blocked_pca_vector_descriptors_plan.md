# Plan: blocked PCA for vector descriptors in `src/feature_selection`

**Status**: agreed design, not yet implemented. Written 2026-08-18 to pick back up without
re-deriving the reasoning.

## Problem

`descriptor_component_matrix` (src/feature_selection/feature_selection.py:78) currently reduces
every descriptor block — scalar or vector — to `min(n_components=5, block_size)` PCA components,
flat over the whole block. For the 6 vector descriptors this is a blind, arbitrary compression:
it treats all raw features in a block as one undifferentiated pool, even when the block is
actually a concatenation of chemically distinct sub-groups.

## What each vector descriptor's raw layout actually is

| Descriptor | Size | Internal structure | Verdict |
|---|---|---|---|
| `AUTOCORR2D` | 192 | 4 methods (ATS, ATSc, MATS, GATS) × 6 atomic properties (mass, vdW volume, electronegativity, polarizability, ion polarity, IState) × 8 lags (topological distance d=1..8) | **Needs blocking** — methods and properties are categorically distinct; lag is the one axis where PCA-style compression within a block is legitimate (ordered, correlated sequence). |
| `MQNs` | 42 | Verified against RDKit's raw source (`Code/GraphMol/Descriptors/MQN.cpp`, not just the Nguyen et al. 2009 paper, since the paper's category order isn't guaranteed to match RDKit's output order): indices 0–11 atom counts, 12–18 bond counts, 19–24 polarity counts, 25–31 degree-topology, 32–41 ring-topology. 5 groups, not the paper's stated 4 (RDKit splits "topology counts" into degree-based and ring-based). | **Needs blocking**, pending a final decision on whether to follow RDKit's native 5-way split (recommended — independently verified) or track down the paper's literal 4-category version. |
| `PEOE_VSA` (14), `SMR_VSA` (10), `SlogP_VSA` (12) | — | Each is already a single semantic axis (one property — charge/MR/logP — binned across VSA surface-area ranges) per the [Landrum VSA post](https://greglandrum.github.io/rdkit-blog/posts/2023-04-17-what-are-the-vsa-descriptors.html). No sub-grouping to exploit. | **No change** — stays one flat PCA block, though whether flat `k=5` is the right size for these (vs. an explained-variance threshold) is a separate, smaller open question, noted but not decided. |
| `CrippenDescriptors` | 2 | 2 independent scalars (total LogP contribution, total MR contribution). | **No change** — already ≤5 features, so PCA already runs as a lossless rotation (`k=min(5,2)=2`), not a reduction. |

## Why CCA, not PCA, for the redundancy check (context, already implemented)

See `src/feature_selection/CLAUDE.md` § "Canonical correlation (CCA), not PCA, for the
correlation-prune step" for the full history — the short version: comparing two descriptors via
Pearson-on-PC1 only compares each one's single dominant axis and can miss/misjudge redundancy
living in later components. `correlation_prune` already uses CCA on the full top-k component sets.
Blocked PCA changes *what* those component sets look like for AUTOCORR2D/MQNs; it doesn't change
that CCA is the comparison method.

## Implementation sketch (not yet built)

1. Add a per-descriptor group definition (name → list of `(group_label, local_feature_indices)`)
   for `AUTOCORR2D` (24 groups: 6 properties × 4 methods, 8 lag-features each) and `MQNs` (5
   groups, per the table above).
2. In `descriptor_component_matrix`, for descriptors with a group definition: run PCA
   independently within each group (compressing the 8 lags per AUTOCORR2D group, or leaving MQN
   groups as-is/lightly compressed since they're already small), then concatenate the per-group
   components into that descriptor's overall component matrix. For descriptors without a group
   definition (the 44 scalars, the 3 VSA descriptors, CrippenDescriptors): unchanged, flat PCA as
   today.
3. Open question: `descriptor_pc1_matrix` (feature_selection.py:98) takes literal PC1 of a flat
   block for VIF, since "VIF is inherently a single-variable-vs-the-rest statistic." Once
   AUTOCORR2D/MQNs are block-structured, "PC1" needs a new definition — candidates: (a) a
   second-level PCA over the concatenated block-PC1s, taking its own PC1 as the meta-representative,
   or (b) keep computing VIF's PC1 from the current flat (unblocked) PCA output, since VIF already
   treats this as a deliberate simplification orthogonal to the redundancy concern CCA handles.
   Leaning toward (b) — simplest, and consistent with the existing docstring's reasoning for why
   VIF doesn't need to track everything CCA does.
   *********ASK ME ABOUT THIS CLAUDE SUPER IMPORTANT*****

## What this change affects downstream, and what it doesn't

Traced against the actual pipeline consumers in `feature_selection.py`:

- **`mutual_info_per_descriptor` (MI)** — consumes `component_map` directly (feature_selection.py:145).
  **Affected**: AUTOCORR2D/MQNs' MI scores could shift, since the components being scored change.
  MI scores feed the tiebreaks in both `correlation_prune` and `vif_prune`.
- **`correlation_prune` (CCA)** — consumes `component_map` directly (feature_selection.py:173).
  **Affected, primary target**: this is the actual redundancy check the blocking is meant to fix.
- **`vif_prune`** — consumes `descriptor_pc1_matrix`'s single PC1 per descriptor
  (feature_selection.py:198). **Affected only if** the open question above is resolved as option
  (a); unaffected if (b).
- **`run_descriptor_rfe`** — operates on **raw, full features** of surviving descriptors
  (feature_selection.py:330: `features = sorted(f for name in remaining for f in
  descriptor_map[name])`), never touches `component_map` or any PCA output at all.
  **Not affected** by how PCA is structured internally — RFE only sees whichever descriptors
  survived `correlation_prune`/`vif_prune` as a gate, then works on their raw columns.
- **`evaluate_descriptor_set`** — same story as RFE (feature_selection.py:254): raw features only,
  never PCA output. **Not affected** directly.

So blocked PCA only changes the **gate** (which descriptors get judged redundant/multicollinear
before RFE ever runs) — not RFE's own math, and not the final CV-R² evaluation, which always
reads real feature columns regardless of how the pruning stages internally represented them.

## Expected performance impact

Per `run_descriptor_rfe`'s own recorded trace (see its docstring and
`src/feature_selection/CLAUDE.md`), the descriptor set already converges to just **`{PEOE_VSA,
SlogP_VSA}` at N=2 (R²=0.346)** — neither AUTOCORR2D nor MQNs is among the strongest descriptors
by RFE's own signal-based elimination. Since blocked PCA only touches AUTOCORR2D/MQNs' redundancy
accounting, and those two descriptors weren't driving the R² ceiling either way, **a large R²
change from this fix is unlikely**. The realistic benefit is a more defensible/correct
`correlation_prune` and (possibly) `vif_prune` decision trail for those two descriptors — not a
big jump in final model performance. It could still matter at the margins: if the current flat
PCA is wrongly flagging AUTOCORR2D or MQNs as redundant against something else (or wrongly
clearing them), fixing that changes which descriptors even reach RFE's starting pool — but given
RFE already discards almost everything down to 2 descriptors regardless, this is more about
correctness/interpretability of the intermediate diagnostic (the "why was X dropped" story) than
about moving the final number.

## Still open before implementing

1. MQNs: paper's literal 4-category grouping vs. RDKit-native 5-way split (leaning RDKit-native,
   since it's independently verified from source rather than assumed from the paper).
2. VIF's PC1-equivalent definition for block-structured descriptors (leaning toward keeping VIF on
   the old flat-PCA PC1, i.e. no change to `vif_prune`'s input).
3. VSA descriptors' flat `k=5`: worth a separate look (explained-variance threshold instead of a
   fixed magic number) — smaller, deferred, not blocking this change.

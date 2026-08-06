# Notebook Review — `01.5_adme_biogen_public_recreation.ipynb` + `01.6_adme_paper_recreation_results.ipynb`

Review checklist. Batches A–I are **complete** and were verified by a full overnight run
(2026-08-03 → 04): `01.5` produced 156 base + 12 tuned result rows; `01.6` re-ran clean (0 error
cells) and regenerated all §5 figures. Remaining work is the **Outstanding** section at the bottom.

> Notebooks are large. To inspect: `json.load` the `.ipynb` and filter by cell `id`; to edit:
> count-asserted raw-text `str.replace` then `json.loads` to validate. New CLAUDE.md convention:
> notebook code favours readability (one statement per line, no semicolon-chaining).

## Status summary
| Batch | What | State |
|---|---|---|
| G | Split into `01.5` (§0–§4) + `01.6` (§5) | ✅ |
| A | ECFP4 as modelling representation (5 featuresets) | ✅ verified |
| B | §2.2 / §2.2c plot styling | ✅ |
| C | §0 consolidation + renames | ✅ (see #19 correction) |
| D | Data-integrity checks | ✅ ran + passed overnight |
| E | Doc / markdown updates | ✅ |
| F | Questions answered + #21 markers | ✅ |
| H | Fit-count prints (part 1) | ✅ · part 2 outstanding |
| I | MPNN2 RobustScaler → QuantileTransformer | ✅ verified |

---

## Batch A — ECFP4 feature thread — ✅ DONE + verified
Featuresets 3→5: `fcfp4`, `rdkit`, `hybrid`, **`ecfp4`**, **`hybrid_ecfp4`** (ecfp4+rdMolDes). Base arm.
- [x] **src** `morgan_fingerprints(use_features=…)` (`False`→ECFP4 matrix) + docstring + `features/CLAUDE.md` + test
- [x] **DECISIONS.md** ADR: ECFP4 promoted from comparison-only to a modelling representation
- [x] **#6** §3: `X_ecfp4` + `X_hybrid_ecfp4`; **#6.5** `section3_feat.pkl` cache (`RECOMPUTE_FEAT`, auto-rebuild)
- [x] **#8** §4.1 `FEATURESETS` → 5; **#17** `01.6` §5.3b + dummy harness extended
- [x] Overnight run: ecfp4 + hybrid_ecfp4 base keys present in checkpoint

## Batch B — Plot styling — ✅ DONE (`01.5`)
Colour = METRIC (Dice=steelblue, Tanimoto=darkorange), style = FINGERPRINT (FCFP4=solid, ECFP4=dotted).
- [x] **#3** §2.2 pairwise-similarity · **#4** §2.2c max-neighbour (same encoding)

## Batch C — §0 consolidation + renames — ✅ DONE
- [x] **#1** No `SPLIT_FILE` refs (already gone)
- [x] **#14** `import json` → `01.5` §0. `TUNED_PARAMS_PATH` left in 4.3a (consistent with RESULTS/PREDICTIONS paths)
- [x] **#2** `fps` → `fcfp4_fps` (generic fn param kept)
- [x] **#20** `hlm_df` → `norm_check_df` + `NORM_CHECK_EP` toggle (`01.6` §5.5)
- [x] **#19 (CORRECTED)** `from scipy import stats` in `01.6` §0. Removing the *local* imports from the
      §5.5 cells was WRONG — §5.4 rebinds `stats` to a DataFrame and shadows the module, which broke the
      overnight `01.6` run. Final fix (below, "shadow bug"): rename the shadowing vars, keep §0 import only.

## Batch D — Data-integrity checks — ✅ DONE + ran overnight
- [x] **#5** §2.4a CSV↔SDF reconciliation report (ran; small std-loss deltas as expected)
- [x] **#12** §4.1 SMILES row-alignment asserts — **passed** (overnight `01.5` completed, so asserts held)
- [x] **#16** answered in Batch F

## Batch E — Doc / markdown updates — ✅ DONE
- [x] **#7** §4.0 runtime note rewritten (stale-proof; points to programmatic counts)
- [x] **#11** §4.2 header (FCNN/BayesianRidge) + `clone(...)` explanation
- [x] **#13a** MPNN3 rationale note in §4.3 · **#13b** RobustScaler resolved via Batch I
- [x] **#9 (as-built)** `n_jobs` consolidated into **`src/hyperparams.py`** (both `n_jobs_model` +
      `n_jobs_cv`; notebook imports them) — NOT the notebook, because `param_base_*` need `n_jobs_model`
      at import. ADR-008 addendum + `MEMORY.md` updated. (Original note said "notebook" — superseded.)
- [x] **#10** dead `if arm == 'tuned'` branch removed from §4.2 base loop

## Batch F — Questions — ✅ answered
- [x] **#11** `clone` · **#15** `_tkey`/`_parse_tkey`/`_kw`/`Xtr`/`fkey` · **#16** `smi_tr`/`smi_te`
- [x] **#18** mpnn2/mpnn3 identical sim-binning (expected) · **#20** 5.5 determinism
- [x] **#21** REVIEW markers on 5.5–5.7 (light code-quality tone). Simplification pass itself = outstanding

## Batch G — Notebook split — ✅ DONE
- [x] `01.6` created (self-contained: §0 + endpoint constants + disk-loader + §5)
- [x] `df` persisted at `01.5` cell 23 → `section4_df.pkl`; `01.6` loads it; §5 removed from `01.5`
- [x] `section4_df.pkl` generated + loaded (overnight run)
- [ ] Minor: `01.5` §4.4 "come back after section 5" note is now cross-notebook (cosmetic)

## Batch H — ✅ DONE
- [x] **Part 1** fit-count prints in §4.2 / §4.2b / §4.3a (programmatic, not hardcoded)
- [x] **Part 2** `SHOW_PLOTS` flag in both notebooks. `01.5`: `render_plotly(fig, name)` saves each
      plotly figure to `figures/<name>.html` and shows only if `SHOW_PLOTS` (3 cells). `01.6`:
      `maybe_show()` gates all `plt.show()`; added `savefig` to §5.5 cells 32/34. Plotly HTML gitignored
      (large, regenerable). Verified: `01.6` re-ran clean; plotly `.show()` works under nbconvert.
      NOTE: default `SHOW_PLOTS=True`; set **False** for unattended nbconvert runs to keep the .ipynb lean.

## Batch I — MPNN2 RobustScaler → QuantileTransformer — ✅ DONE + verified
- [x] §4.1 splits `X_train_qt`/`X_test_qt` (rdkit fs, fit on raw X_train, QT uniform, seed 42)
- [x] §0 import `QuantileTransformer`; MPNN2 repointed in §4.2b/§4.3a/§4.3b (MPNN1/MPNN3 untouched)
- [x] `mpnn.py` docstring + DECISIONS.md ADR + §4.2b residual-limitation note + migration cell
- [x] Overnight run: migration ran, `MPNN2` (QT) + `MPNN2_robustscaler` both in checkpoint
- [done now i think ] **Deferred:** MPNN4 = QT-uniform on the 200 unnormalized rdkit_2d (clean feature-count control)

## Tuning scope (decided 2026-08-03, ran overnight) — ✅ DONE
- [x] Tuned arm = **RF, LightGBM (hybrid) + MPNN3 only** (`TUNE_CLASSICAL=['RF','LightGBM']`,
      `MPNN_TUNE_MODELS=['MPNN3']`, `TUNE_FCNN=False`, `TUNE_FEATURESETS=['hybrid']`; §4.3b scoped).
      All 12 keys already cached → eval-only, no re-tuning. Verified: 12 tuned rows in checkpoint.

## `stats` shadow bug — ✅ FIXED (regression from #19)
- [x] §5.4 `stats` DataFrame → `bin_stats`; Fig 7 `stats` list → `fig7_stats`; both guard re-imports
      removed; §0's `from scipy import stats` now stands alone. `01.6` re-ran clean.
- [x] Cell-id normalization on both notebooks (silences nbformat MissingIDFieldWarning)

---

## Done post-commit (2026-08-04)
- [x] **Point 2** MPNN1 added to tuning scope (`MPNN_TUNE_MODELS=['MPNN1','MPNN3']`). NOTE: MPNN1
      params already cached (full) → §4.3a skips re-tuning, §4.3b evaluates it (that eval = the run cost).
- [x] **#3** dropped dead `'MPNN2'` key from `FIG7_MODEL_FS`.
- [x] **#2** readability: unchained the semicolon lines I'd added (§3 cache ×2, §4.2b MPNN print ×1).
- [x] **#1 / Batch H part 2** plot flag + plotly HTML saving (see Batch H above).

## Done 2026-08-04 (round 2)
- [x] **§5.5 simplification** — merged cell 32's duplicate `r_vals` loops; removed 2 dangling-var dev
      cells (37/40); cleaned a leftover comment. `01.6` re-ran clean. (§5.6/§5.7 already clean.)
- [x] **§5.7 → df_sdf** (single source w/ modelling): §2.2 KEPT on CSV (matches paper, plot-only, never
      touches modelling — confirmed). §5.7 Table 2 now from `df_sdf` (persisted `section4_df_sdf.pkl`,
      loaded in `01.6`). Verified counts: model endpoints −1 (standardisation), PPB +augmentation.

## OUTSTANDING
1. DONE - **MPNN4 control** — QT-uniform on the 200 *unnormalized* rdkit_2d (vs MPNN2's 316 rmoldes = feature
   count; vs MPNN3's CDF = normalization). Needs: unnormalized rdkit_2d featurizer, §3 compute, §4.1
   MPNN-only split+QT, §4.2b/§4.3a/§4.3b feature-source mapping, re-run. IN PROGRESS.
2. **§4.4 scaffold split** — pre-existing TODO in `01.5`; user parking alongside data-quantity/noise work.

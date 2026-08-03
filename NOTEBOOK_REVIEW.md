# Notebook Review — `notebooks/01.5_adme_biogen_public_recreation.ipynb`

Working checklist for the full review. Items grouped into **dispatchable batches** so each
can be handed to a fresh Claude CLI session without collisions. Ordering matters only where
noted (Batch A first — it changes featureset counts that later prose describes).

> Notebook is ~110 cells and too large to Read in one pass. To inspect: `json.load` the
> `.ipynb` and filter by cell `id`; to edit: count-asserted raw-text `str.replace` then
> `json.loads` to validate. (See MEMORY.md "Known Infrastructure Issues".)

## Agreed execution order (2026-08-03)
1. **F #21** — trivial markers
2. **B, C, D** — safe, independent (parallelizable across sessions)
3. **G** — do it early (before A): not quick (~1 session) but high-leverage; shrinks the
   file every later batch must parse. After G, A spans both notebooks (clean checkpoint boundary).
4. **A** — ecfp4, now on the smaller split notebooks
5. **E + H together** — post-A doc updates. Make **H programmatic** (print fit count from
   `len(FEATURESETS)×…`) so it never goes stale as featuresets change.

---

## Batch A — ECFP4 feature thread — ✅ DONE (decisions: base-arm only, + ecfp4-hybrid)
Featuresets 3→5: `fcfp4`, `rdkit`, `hybrid`, **`ecfp4`**, **`hybrid_ecfp4`** (ecfp4+rdMolDes).
- [x] **src**: `morgan_fingerprints` gained `use_features=True` param (`False`→ECFP4 numpy matrix);
      docstring, `features/CLAUDE.md`, and a new sanity test updated. 122 tests pass.
- [x] **DECISIONS.md**: ADR added — ECFP4 promoted from comparison-only to a modelling representation.
- [x] **#6** §3 (cell 51): `X_ecfp4` + `X_hybrid_ecfp4` added to `feat`.
- [x] **#6.5** §3 cache: `section3_feat.pkl`, `RECOMPUTE_FEAT` flag, auto-rebuild if keys missing.
- [x] **#8** §4.1 (cell 58): `FEATURESETS` → 5. Splits auto-expand.
- [x] **#17** `01.6` §5.3b (cells 18/19) + dummy harness (cell 11) extended to 5 featuresets.
- [ ] **USER re-run:** §3 (rebuilds cache+splits) → §4.2 base loop (checkpointed → +2 fs × 5 models
      × 4 ep = 40 new base keys) → `01.6` §5.3b.

## Batch B — Plot styling (independent, safe) — ✅ DONE (in 01.5)
Final encoding (per user): colour = METRIC (Dice=steelblue, Tanimoto=darkorange),
line style = FINGERPRINT (FCFP4=solid, ECFP4=dotted). Every curve distinct.
- [x] **#3** §2.2 pairwise-similarity plot (cell 30)
- [x] **#4** §2.2c max-neighbour plot (cells 32+33) — same encoding for consistency

## Batch C — Section-0 consolidation + renames (mechanical) — ✅ DONE
- [x] **#1** No `SPLIT_FILE` refs found — already removed by user. Nothing to do.
- [x] **#14** `import json` moved to `01.5` §0 cell 2 (removed from 4.3a). `TUNED_PARAMS_PATH`
      LEFT in 4.3a on purpose — consistent with `RESULTS_CSV`/`PREDICTIONS_PKL` (defined in 4.2,
      not §0). Centralising all three checkpoint paths to §0 is a separate optional cleanup.
- [x] **#19** `from scipy import stats` moved to `01.6` §0 cell 3 (removed from §5.5 cells 32 & 34).
- [x] **#2** Global `fps` → `fcfp4_fps` (`01.5` cells 29, 32). Generic function param
      `max_neighbor_sims(fps, ...)` intentionally kept — it takes both fcfp4 and ecfp4 fps.
- [x] **#20** `hlm_df` → `norm_check_df` + `NORM_CHECK_EP='HLM'` toggle (`01.6` §5.5) — swap one
      value to check SOL/RLM/MDR1. (`norm_df` was taken by the shape-stats cell.)

## Batch D — Data-integrity checks (additive) — ✅ DONE (cells written; USER MUST RUN)
Key finding: **model features (§3) come from `df_sdf` (SDF), not CSV `df`**. CSV `df` is only used
for §2.1 stats, §2.2 similarity plots, §5.7 Table 2.
- [x] **#5** New §2.4a reconciliation cell (report): CSV vs SDF molecules per endpoint on a
      `standardize()`-canonical key. Expect small CSV-only (std losses) for HLM/MDR1/SOL/RLM,
      large SDF-only for PPB (augmentation). Non-failing report — interpret after running.
- [x] **#12** New assertion cell after §4.1 splits: SMILES identical across featuresets +
      `morgan_fingerprints(smiles_train) == X_train`. Guarantees the row-alignment MPNN2/3
      `column_stack` relies on. Hard asserts — construction-guaranteed to pass.
- [x] **#16** Answered in Batch F (was a question, no edit).
- [ ] **USER:** run §2.4a (#5) and the §4.1 check (#12) once to confirm.

## Batch E — Doc / markdown updates (DO AFTER Batch A)
Depends on final featureset count + ARMS decision.
- [ ] **#7** Rewrite 4.0 runtime note (the 4×3×5×2=120 math changes with ecfp4)
- [ ] **#11** Update 4.2 header (FCNN now included) + explain `clone(...)` (answered in Batch F)
- [ ] **#13** Add MPNN3 rationale note in 4.3; verify RobustScaler applied to mpnn2 vs mpnn3
- [ ] **#9** Consolidate `n_jobs` to ONE place (notebook, not `hyperparams.py`) + update
      `DECISIONS.md` (ADR-008) and `MEMORY.md`
- [ ] **#10** Tidy `ARMS = ('base',)` — the 'tuned' branch is dead in 4.2 (produced by 4.3b)

## Batch F — Questions (answered inline in review response; no edits except #21 marker)
- [x] **#11** what `clone(paper_models[model_name])` does
- [x] **#15** `_tkey` / `_parse_tkey` / `_kw` / `Xtr` / `fkey` explained
- [x] **#16** why `smi_tr`/`smi_te` in 4.3b (vs §3)
- [x] **#18** mpnn2 & mpnn3 identical similarity binning — expected?
- [x] **#20** does kernel reset / seed change 5.5 results?
- [x] **#21** REVIEW markers added to 5.5, 5.6, 5.7 (now in `01.6`). Reworded to a light
      **code-quality** note (can it be simplified / vars reused?) — NOT "logic unverified".
      The actual simplification pass is a separate future task on 5.5–5.7.

## Batch G — Notebook split (NEW, structural) — ✅ DONE (01.5→73 cells, 01.6→46 cells)
- [x] Created `notebooks/01.6_adme_paper_recreation_results.ipynb` (46 cells vs 112):
      §0 setup + §0.1 endpoint constants (`ENDPOINTS`/`ENDPOINT_COLS`/`MODEL_ENDPOINTS`,
      the only cross-section deps) + disk-loader + §5. Verified self-contained (AST scan, 0 gaps).
- [x] `01.5` cell 56 now also `joblib.dump(df, 'section4_df.pkl')` (§5.7 Table 2 needs raw df;
      df is not reassigned after cell 56, so this is faithful to the monolithic run).
- [x] `01.6` loader loads `df` from that pkl.
- [x] Deleted §5 (cells 73–111) from `01.5` → 73 cells. `df` dump relocated to cell 23
      (df immutable after load). User's `#fig.show()` edits preserved.
- [x] **Before 01.6 runs:** run `01.5` top → §2.0 (cell 23) ONCE to generate `section4_df.pkl`
      (not yet on disk). Other checkpoint pkls already exist.
- [ ] Stale note: `01.5` §5 harness markdown ("run 0–section 3") — now lives in `01.6` as 5.pre,
      already rewritten there. The `01.5` §4.4 "come back after section 5" note is now cross-notebook.

## Batch H —
- Add number of fits to model training, eval, tuning sections so its clear why it might take long to run from fresh
- I put 3 ';' after update layout and commented out fig.show() in 01_5 notebook, must be a better way to hide/show plots? maybe a flag for them to be shown/hidden? Might help if we saved the plots to the machine, that way they can always be hidden and I can change the flags as and when its needed? I noticed none of the plotly plots are saved? I noticed that when the plots are showing, it makes it hard to save my notebook.


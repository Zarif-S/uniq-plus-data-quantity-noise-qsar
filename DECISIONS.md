# Decisions - Architectural Decision Records (ADR)

An ADR captures a decision made during the project, the reasoning behind it, and what alternatives were considered. Decisions are logged here to avoid revisiting settled questions and to provide a trail for writeup and future work.

---

## ADR-001 — Incorporate PrO Posteriors as Framework Reference, Not Full Experiment

**Date**: 2026-07-10
**Status**: Decided
**Decider**: Zarif

---

### Context

During Phase 1, the paper *"Predictively Oriented Posteriors"* (Fong & Holmes, 2025; arXiv:2510.01915) was identified as potentially relevant to the UNIQ+ research questions. The paper proposes a shift in Bayesian inference from maximising certainty about parameters to maximising predictive accuracy — producing posteriors that remain spread out under model misspecification rather than collapsing to a point.

---

### How PrO connects to UNIQ+ research

The connections are genuine and non-trivial:

1. **QSAR models are inherently misspecified.** Molecular fingerprints and 2D descriptors are coarse summaries of complex biology. The models we test (RF, XGBoost, LightGBM, linear) are all misspecified in the PrO sense — they cannot fully capture the data-generating process. PrO is specifically designed for this regime.

2. **Data quantity experiments (Phase 2) directly interact with PrO's core property.** Standard posteriors collapse to a point as N grows, whether or not the model is correct. PrO posteriors remain meaningfully spread under persistent misspecification. This means that as learning curves flatten, PrO provides a theoretically principled explanation: the model has hit its misspecification ceiling, not a data ceiling.

3. **Noise injection (Phase 4) induces misspecification.** When labels are corrupted with Gaussian noise or shuffled, the model's assumed data-generating process diverges from reality — exactly the regime where PrO posteriors preserve "irreducible uncertainty" rather than overconfidently collapsing. PrO's irreducible uncertainty could serve as a diagnostic for noise severity.

4. **Split strategy (Phase 3) affects effective misspecification.** Chemotype-based splits expose models to structurally novel test compounds; the model is more misspecified relative to the test set. A PrO lens predicts that uncertainty would be higher and less reducible under chemotype splits vs. random splits — a testable hypothesis, though not tested in this project.

5. **Model criticism.** PrO posteriors that remain multimodal despite large N signal hidden sub-groups (different mechanisms of action, different assay conditions). This is relevant for the ADME dataset where the 6 endpoints likely have partially distinct chemical drivers.

---

### Why full implementation is not suitable for this project

1. **No existing implementation.** The paper was published October 2025. There is no established Python package. A correct implementation requires deriving and coding the PrO update rule from scratch, which is a research contribution in its own right.

2. **Computational cost.** Proper posterior estimation (even via approximate inference) is significantly slower than the point-estimate ML models in scope. Running PrO across learning curve fractions × noise levels × 6 endpoints × 2 datasets × 3 model types would be computationally prohibitive within a 6-week timeline.

3. **Scope and identity mismatch.** UNIQ+ is an empirical, data-centric study — it measures what happens to standard ML models as data conditions change. Fully implementing PrO would pivot the project toward Bayesian methodology research. That is a different paper.

4. **Timeline.** Phases 1–4 already account for all 6 weeks. Adding a full Phase 5 for novel Bayesian inference would require cutting noise experiments or writeup time, both of which are higher priority for the stated research goals.

---

### Decision

Incorporate PrO in two lightweight ways:

1. **`BayesianRidge` as a fourth baseline model (Phase 1).** `sklearn.linear_model.BayesianRidge` is a standard Bayesian linear model with zero additional implementation cost. It provides a natural Bayesian comparison point: if the linear relationship holds, BayesianRidge should match or exceed Linear Regression; if the data is complex, the gap between BayesianRidge and tree-based models illustrates the misspecification problem PrO describes. This gives empirical grounding for PrO-informed discussion in the writeup at no meaningful cost.

2. **PrO as a theoretical frame in the writeup (Phase 4).** The noise and data-quantity results are interpreted through PrO's lens: performance degradation is reframed as "entry into a misspecification regime" rather than simply "RMSE increase." This adds theoretical depth and positions the results within current Bayesian ML literature without requiring new experiments.

**Full PrO implementation is deferred to future work** (see below).

---

### Future work

If UNIQ+ is extended or developed into a publication, PrO is a strong candidate for a dedicated experiment:

- Implement PrO using the authors' formulation for a linear QSAR model
- Compare PrO posterior spread vs. standard Bayes as N decreases (Phase 2 equivalent)
- Use PrO irreducible uncertainty as a noise diagnostic alongside RMSE (Phase 4 equivalent)
- Test whether PrO correctly identifies multimodal structure in ADME endpoints with distinct chemical drivers

This would constitute a novel contribution to both Bayesian ML and computational drug discovery.

---

**Reference**: Fong, E. & Holmes, C. (2025). *Predictively Oriented Posteriors.* arXiv:2510.01915. [https://arxiv.org/pdf/2510.01915](https://arxiv.org/pdf/2510.01915)

---

## ADR-002 — Per-Endpoint Filtering Over Imputation for Missing ADME Values

**Date**: 2026-07-13
**Status**: Decided
**Decider**: Zarif

---

### Context

The ADME dataset has highly variable missingness across its 6 endpoints:
- HLM: 12.3% missing, RLM: 13.3% missing
- MDR1: 25.0% missing, SOLUBILITY: 38.3% missing
- PPB_HUMAN: 94.5% missing, PPB_RAT: 95.2% missing

Before training baseline models, a strategy for handling NaN values was required. Two main options were considered: imputation and per-endpoint filtering.

---

### Alternatives Considered

**Complete-case filtering** (drop any row missing any endpoint): retains only ~180 rows (~5% of the dataset) because PPB missingness is near-total. Discards the vast majority of valid HLM/RLM/MDR1/SOLUBILITY measurements. Rejected.

**Imputation** (mean, median, or k-NN fill): fills NaN values before training a single joint model across all endpoints. Rejected — see reasoning below.

**Per-endpoint filtering** (train each model independently on its own non-NaN rows): each of the 6 models sees only compounds with a measured value for its target endpoint. Accepted.

---

### Why Imputation Is Incorrect Here

1. **Missing values are structural, not random.** A NaN in HLM means the compound was never sent to the human microsome assay — not that it has an average clearance. Imputing would be fabricating measurements.

2. **Missingness pattern is batch-driven.** HLM and RLM are measured together; PPB_HUMAN and PPB_RAT are measured together. These are separate experimental batches, not random omissions. Imputing across batches would introduce systematic cross-assay contamination.

3. **Log-transformed biological values have meaningful scale.** Mean imputation on log-clearance would bias the imputed value toward the centre of the assay range, which is not scientifically meaningful for untested compounds.

4. **Independent endpoints in ADME.** ADME endpoints have distinct chemical drivers — lipophilicity dominates PPB, metabolic stability dominates HLM/RLM, polar surface area dominates MDR1. A model for HLM has no principled basis for filling PPB values, even with cross-endpoint correlation.

---

### Decision

Train 6 independent models, one per endpoint. Each model is trained and evaluated exclusively on compounds with a non-NaN value for that endpoint. Effective training set sizes:

| Endpoint | N for model |
|----------|-------------|
| HLM      | ~3087       |
| RLM      | ~3054       |
| MDR1     | ~2642       |
| SOL      | ~2173       |
| PPB_H    | ~194        |
| PPB_R    | ~168        |

PPB models (~170–190 samples) will have wider uncertainty than HLM/RLM models (~3000 samples). This is an honest reflection of the experimental reality, not a limitation to be papered over with imputation.

---

### Implications for Later Phases

- **Phase 2 (learning curves)**: each endpoint's learning curve starts from its own N, not a shared pool.
- **Phase 4 (noise injection)**: noise is added per-endpoint to that endpoint's non-NaN subset only.

---

## ADR-003 — Discard `val` Rows in PDE10A Baseline Evaluation

**Date**: 2026-07-14
**Status**: Decided
**Decider**: Zarif

---

### Context

The PDE10A dataset ships with 7 pre-defined split columns. Each row is labelled `train`, `test`, or `val`. When building baseline models, a decision was needed on what to do with `val` rows — they cannot silently be included in either training or test without consequences.

---

### Alternatives Considered

**Include `val` in training**: increases training set size, but conflates the purpose of the split. The original authors defined `val` separately; merging it into `train` would deviate from the intended experimental design.

**Evaluate on `val` instead of `test`**: defeats the purpose of a held-out test set and introduces optimistic bias if `val` is later used for model selection.

**Include `val` in test**: inflates test set size and mixes two partitions with potentially different distributional properties (e.g. temporal `val` years fall between `train` and `test` chronologically).

**Discard `val` for baseline evaluation**: `val` rows are excluded from both training and evaluation. Only `train` → `test` is used. Accepted.

---

### Reasoning

Baselines are a fixed benchmark, not a tuning exercise. No hyperparameter search, early stopping, or model selection is performed at this stage, so there is no use for `val` rows yet. Holding them out now means they remain available — uncontaminated — for:

- **Phase 3 (deep learning)**: ChemProp and DeepChem require a validation set for early stopping.
- **Phase 2 (learning curves)**: if sub-sampling of `train` is needed, `val` provides an independent check that the learning curve is not overfitting to test.

Using `val` prematurely would either waste it or compromise the integrity of later experiments that genuinely need it.

---

### Decision

`get_split` returns only `train` and `test` partitions. `val` rows are silently dropped. This is enforced at the splitting module level (see `src/splitting/`) and documented in SYNC-007.

---

### Implications for Later Phases

- **Phase 3 (deep learning)**: revisit `get_split` to optionally return `val` for early stopping.
- **Phase 2 (learning curves)**: `val` may be used as an independent check if sub-sampling `train`.

---

---

## ADR-004 — Fixed Validation Set Over k-Fold CV for Hyperparameter Tuning

### Context

Hyperparameter tuning for LightGBM and RandomForest requires a held-out set to score candidate configurations. The standard choice is k-fold cross-validation (`cv=5`). An alternative is a single fixed validation set carved out of the training data (20% hold-out, same `random_state` as the train/test split).

### Options Considered

**k-Fold CV (`cv=5`)**: Each fold uses a different 20% of training data as validation. More robust estimate of generalisation; standard practice.

**Fixed val set (PredefinedSplit, 20%)**: A single held-out slice is fixed for the entire hyperparameter search. Slightly higher variance in the score estimate, but the val set is an explicit, controllable object.

### Decision

Fixed val set via `PredefinedSplit`. The function signature is `tune_lightgbm(X_train, y_train, X_val, y_val, ...)` and `tune_rf(X_train, y_train, X_val, y_val, ...)`. After selecting best params, the model is refitted on `X_train + X_val` before returning.

### Rationale

The decisive reason is **Phase 5b**, which compares:
- tuning with a *noisy* validation set vs
- tuning with a *clean* validation set

at representative dataset sizes (full N, 25%, 5%). This sub-experiment requires explicit, reproducible control over exactly which molecules are in the val set and whether noise has been injected into them. With k-fold CV the val set rotates across folds — you cannot cleanly label it as "noisy" or "clean" without injecting noise into all folds simultaneously, which conflates the experiment.

A fixed val set makes the val partition a first-class object that the experiment loop can manipulate independently of the train set.

Secondary reasons:
- **Speed**: `PredefinedSplit` with one fold is 5× faster than `cv=5`, relevant when re-tuning per condition across many experiment cells.
- **Consistency**: the same val molecules are held out in every tuning call, so hyperparameter scores are comparable across conditions.

### Implications

- The 20% val split is done in the notebook before calling `tune_*`, using `train_test_split(X_train, y_train, test_size=0.2, random_state=SEED)`.
- For Phase 5b: the noisy-val arm injects noise into `y_val` before passing it to `tune_*`; the clean-val arm passes the original `y_val`. The test set remains clean in both arms.
- `src/tuning/CLAUDE.md` function signatures updated to reflect `X_val, y_val` parameters.

---

## ADR-005 — Label Noise Model Definitions

**Date**: 2026-07-21
**Status**: Decided
**Decider**: Zarif

---

### Context

Three types of label noise are injected into `y_train` for Phase 5 and Phase 5b experiments, following the taxonomy of Landrum & Riniker. Each noise type models a distinct real-world assay imperfection. The exact formulations need to be pinned to avoid ambiguity in the writeup.

All noise levels are expressed as fractions of `std(y)` for the endpoint being corrupted, making them scale-invariant across HLM, MDR1, SOL, and RLM.

---

### Formulations

**1. Gaussian noise** (`add_gaussian_noise`) — intra-assay variability

```
σ = sigma_frac × std(y)
y_noisy[i] = y[i] + ε[i],   ε[i] ~ N(0, σ²)  for all i
```

Independent per-label additive noise. Models random measurement error within a single experimental batch (pipetting variability, instrument drift). Levels: `sigma_frac ∈ {0.0, 0.1, 0.3, 0.5, 1.0}`.

**2. Systematic bias** (`add_systematic_bias`) — inter-assay bias

```
bias = bias_frac × std(y)
S[i] ~ Bernoulli(0.5) independently per label   (random 50% selection)
y_noisy[i] = y[i] + bias   if S[i] = 1
y_noisy[i] = y[i]          if S[i] = 0
```

A constant positive shift applied to a random half of the training labels. Models inter-assay bias — e.g. two labs running the same assay with a systematic offset between instruments. The shift is one-directional (always positive), so it introduces a net upward shift in the training distribution mean. Levels: `bias_frac ∈ {0.0, 0.1, 0.3, 0.5, 1.0}`.

**3. Gross errors** (`add_gross_errors`) — annotation errors

```
k = max(1, floor(error_frac × N))
idx ← k indices sampled without replacement from {0, …, N-1}
y_noisy[i] = U[y.min(), y.max()]   for i ∈ idx
y_noisy[i] = y[i]                  for i ∉ idx
```

Replaces `k` labels with values drawn uniformly from the observed endpoint range. Models annotation errors — transcription mistakes, sample mix-ups, or wrong structure-activity assignments. Clamped to `[y.min(), y.max()]` by design to avoid out-of-distribution outliers. Levels: `error_frac ∈ {0.0, 0.01, 0.05, 0.10, 0.20}`.

---

### Shared Invariants

- `y_train` is never mutated — all functions return a new array
- `y_test` is never corrupted — noise is applied to training labels only
- All functions are reproducible given `random_state`

---

### Reference

Landrum, G. & Riniker, S. (taxonomy). Implemented in `src/noise/noise.py`.

---

## ADR-006 — MAE as Hyperparameter Tuning Scoring Metric

**Date**: 2026-07-21
**Status**: Decided
**Decider**: Zarif

---

### Context

`RandomizedSearchCV` requires a scalar scoring function to rank hyperparameter candidates. The natural choices for regression are MSE/RMSE (squared error) or MAE (absolute error). This applies to `tune_lightgbm` and `tune_rf` — the two models that undergo HP search in Phases 3–5b.

---

### Decision

Use `scoring="neg_mean_absolute_error"` (MAE) in `RandomizedSearchCV` for both LightGBM and RF.

---

### Rationale

The tuning functions are used in two contexts:

1. **Phase 3 (clean data reference tuning)** — noise is absent; MSE and MAE would select similar configurations
2. **Phases 4–5b (re-tuning under noise)** — `y_train` contains corrupted labels

In context 2, MSE is problematic: squared error amplifies the contribution of corrupted labels quadratically. A small number of gross errors or large Gaussian draws dominates the validation score, steering HP search away from configurations that generalise on clean labels. MAE treats all residuals linearly, so corrupted labels degrade the tuning signal proportionally rather than disproportionately.

Using MAE consistently across both contexts (rather than switching metric by phase) keeps the tuning behaviour comparable and avoids introducing a confound between the clean and noisy arms.

---

### Fairness of baseline vs tuned comparison

The MAE scoring applies only to HP selection, not to the training objective. Both baseline and tuned models train with squared error loss (LightGBM: `objective='regression_l2'`, RF: `criterion='squared_error'`). The only difference between arms is which hyperparameters are used — which is precisely the confound the experiment is designed to measure. There is no metric confound between arms.

An alternative design would switch the training objective to MAE across all models, making training loss consistent with the HP selection metric. This was considered and rejected: Ridge and BayesianRidge do not support MAE as a training objective, so a consistent switch is not possible without dropping those models; and MSE-trained models are standard in QSAR benchmarks, making results more directly comparable to published work.

---

### Scope

Only `tune_lightgbm` and `tune_rf` are affected. XGBoost, BayesianRidge, and MeanPredictor are not tuned and use their library defaults for training loss (squared error throughout).

The MPNN3 tuned arm uses `metric='mae'` in ChemProp's early stopping for the same reason (see `_run_mpnn2` in `03_adme_experiments.ipynb`); the MPNN3 baseline arm uses ChemProp's default `metric='rmse'`. Note that in ChemProp 1.6.1 `--metric` controls the early stopping criterion only — the training loss is hardcoded to MSE for regression regardless of this flag. So MPNN3 trains with MSE in both arms.

---

---

## ADR-007 — Paper Recreation Methodology Decisions (Fang et al. 2023)

**Date**: 2026-07-22
**Status**: Decided
**Decider**: Zarif

---

### Context

Notebook `01.5_adme_biogen_public_recreation.ipynb` reproduces Fang et al. (2023). Several methodology choices required explicit decisions where the paper text was ambiguous, contradicted its own code, or where our implementation differed mechanically but not substantively.

---

### Decisions

**Fingerprint radius — follow code over paper text**
Paper text states "radius 4 (FCFP4)" — a contradiction (FCFP4 means diameter=4, i.e. radius=2). Source code (`ADME_ML_public.py` line 187) uses `radius=2, nBits=1024, useFeatures=True`. We follow the code: radius=2, FCFP4. FCFP4 remains the fixed featurizer for modelling — do not swap it for ECFP4 there. (Update 2026-07-29: ECFP4 is now used in section 2.2's similarity-distribution plot, purely as a comparison series against FCFP4 — not for any ML features. Same `fcfp4_bit_vectors()` call with `use_features=False`; ECFP4/FCFP4 differ only in that one RDKit flag, no separate function.)

**ECFP4 promoted from comparison-only to a modelling representation (2026-08-03)**
Supersedes the "not for any ML features" clause in the fingerprint-radius decision above. ECFP4 is
now also a modelling featureset, used in §5.3b (Paper's Fig 5) to study the effect of molecular
representation on model performance. Two new featuresets are added alongside `fcfp4`/`rdkit`/`hybrid`:
`ecfp4` (1024 ECFP4 bits) and `hybrid_ecfp4` (ECFP4 + rdMolDes, 1340). Numpy ECFP4 matrices come from
`morgan_fingerprints(smiles, use_features=False)` (new `use_features` param; default `True` = FCFP4,
unchanged). FCFP4 remains the **primary** featurizer — the paper's `hybrid` stays fcfp4+rdkit. The new
featuresets run the **base arm only** for now (tuning can be added later). This reverses the earlier
comparison-only scope deliberately, to broaden the representation comparison.

**Similarity metric — Sørensen-Dice, not Tanimoto**
Paper methods state Sørensen-Dice explicitly. Using Tanimoto gave mean=0.167 ± 0.059; switching to Dice gave 0.282 ± 0.083, matching the paper's reported 0.28 ± 0.08 exactly. Use `DataStructs.BulkDiceSimilarity` throughout.

**Mol standardization — match paper's standardize() exactly**
Four steps in order: Cleanup → FragmentParent → Uncharge → TautomerEnumerator.Canonicalize. Implemented in `src/preprocessing/preprocessing.py`. Causes small compound losses (−1 per endpoint for HLM/MDR1/SOL/RLM) due to deduplication after canonical SMILES change — expected, paper would have encountered the same.

**rdMolDes descriptor set — use paper's hand-picked 316, not full RDKit list**
Paper used a specific subset of 316 rdMolDescriptors calls (not `Descriptors.descList`). Implemented in `src/features/features.py::rdmoldes()`. 9 of 316 require SDF conformers (geometry-dependent) — this drives the decision to load from SDF rather than CSV SMILES.

**MPNN featurization — rdkit_2d_normalized (descriptastorus, 200 features), not rdMolDes**
The paper's MPNN uses `--features_generator rdkit_2d_normalized` (ChemProp calls descriptastorus internally). This is a different descriptor set from rdMolDes (316). Our `rdkit_2d_features()` calls descriptastorus directly — same 200 features. Do not normalize rdMolDes as a substitute; they are different descriptor sets.

**MPNN3 upstream scaling — QuantileTransformer(uniform), not RobustScaler (2026-08-03)**
- **Intent**: MPNN3 exists to isolate one question — *does swapping the 200-feature rdkit_2d_normalized set for our 316 rmoldes change MPNN performance?* MPNN2 is the paper-faithful variant (graph + ChemProp's own rdkit_2d_normalized, CDF-normalized by descriptastorus) and must stay unchanged.
- **Confound (the problem)**: MPNN3 previously fed RobustScaler'd rmoldes (the shared `X_train_scaled`). That differs from MPNN2 in *two* ways at once: feature set (316 vs 200) **and** normalization (RobustScaler — linear, unbounded tails — vs CDF — bounded [0,1], uniform). RobustScaler leaves AUTOCORR2D (192 cols) and MQN (42) with heavy unbounded tails that can destabilise the FFN, plausibly handicapping MPNN3 for reasons unrelated to feature *content*. It also mismatched the paper's philosophy (the paper applies RobustScaler only to the traditional ML models, never the MPNN).
- **Fix**: scale MPNN3's 316 rmoldes with `QuantileTransformer(output_distribution='uniform', n_quantiles=min(1000, n_train), subsample=10000, random_state=42)`, fit on `X_train` only (transform val/test), keeping `--no_features_scaling`. QT-uniform is the closest analogue to rdkit_2d_normalized's CDF (percentile → uniform [0,1], bounded, outlier-robust). Applied upstream in the §4.1 splits (`X_train_qt`/`X_test_qt`, rdkit featureset only) — MPNN1/MPNN2 and the classical models' RobustScaler are untouched.
- **Residual limitation (logged, not fixed)**: QT is *empirical* and fit on our ~1–3k training molecules; descriptastorus's CDF is *parametric*, fit on a large external corpus (so it extrapolates, whereas QT clamps out-of-range test values to 0/1). Same family, minor mechanism difference — acceptable.
- **Kept old run**: the RobustScaler MPNN3 is preserved as model `MPNN3_robustscaler` (featureset `graph_rdkit`) via a one-time checkpoint migration — the RobustScaler-vs-QT delta is itself a reportable result.
- **MPNN4 — the feature-count control (implemented 2026-08-04)**: MPNN3/MPNN2 confound two variables at once (feature set *and* normalization); MPNN4 disentangles them. It is QT-uniform on the 200 *unnormalized* rdkit_2d descriptors (`rdkit_2d_features(smiles, normalized=False)` → descriptastorus `rdDescriptors.RDKit2D()`, verified to return the *same 200* descriptor names as the normalized version, just un-CDF'd). Two clean single-variable contrasts result:
  - **MPNN4 vs MPNN3** — same transform (QT-uniform), differ only in feature *set*: 200 rdkit_2d vs 316 rmoldes.
  - **MPNN4 vs MPNN2** — same 200 rdkit_2d features, differ only in *normalization*: empirical QT-uniform (train-fit) vs descriptastorus parametric CDF.
  MPNN2 stays untouched (paper-faithful). MPNN4 features live under featureset label `graph_rdkit2d_raw`, built MPNN-only in §4.1 (kept out of `FEATURESETS` so the base loop never runs classical models on it) with the same shuffle(42)+split(84) seeds as the shared fcfp4 SMILES (row alignment asserted). Wiring uses `MPNN_FEATURE_SOURCE = {'MPNN3':'rdkit','MPNN4':'rdkit2d_raw'}` (§4.2b/§4.3a/§4.3b). Run as **base arm only** — not added to `MPNN_TUNE_MODELS`, since a feature-count control needs no tuned variant. The same QT-vs-CDF *residual limitation* logged above for MPNN3 applies to the MPNN4-vs-MPNN2 contrast (empirical train-fit QT vs parametric external-corpus CDF). Raw RDKit2D can emit ±inf; the featurizer clamps non-finite values (NaN→0.0, inf→largest-finite) so the rank-based QT never sees inf. On the current ADME data no molecule actually triggers this (all raw descriptors finite, verified).

**Cross-validation — GridSearchCV with RepeatedKFold, random fold assignment**
Paper used `GridSearchCV` with `RepeatedKFold(n_splits=5, n_repeats=3, random_state=128)`. Random fold assignment — not scaffold-based for now, todo later. Temporal splits not applicable to public dataset (no time index).

**Scaling — RobustScaler for SVM and Lasso only, fit on X_train**
RobustScaler fit_transform on X_train, transform on X_test. Not applied to RF, XGBoost, LightGBM (tree-based, scale-invariant). y values never scaled (already log-transformed in raw data).

**Hybrid feature construction — np.hstack([X_fcfp4, X_rdkit]), FCFP4 first**
Paper builds hybrid row-by-row via string lists and a CSV round-trip. We use `np.hstack` — mechanically different but produces the same (N, 1340) float64 matrix with the same column order (FCFP4 columns 0–1023, rdMolDes columns 1024–1339).

---

## ADR-008 — Single-Layer Parallelism for Paper-Recreation Tuning (`n_jobs`)

**Date**: 2026-07-30
**Status**: Decided
**Decider**: Zarif

---

### Context

Tuning the paper-recreation regressors (`tune_paper_model` → `GridSearchCV`; `model_validation` → `cross_val_score`) oversubscribed the CPU. A single-`(endpoint, featureset)` RF tune ran >1 h at ~840% CPU on an 8-core machine — compute-bound, but far slower than the work warranted.

Root cause: two nested parallelism layers both set to `n_jobs=-1`. The outer `GridSearchCV`/`cross_val_score` spawned ~8 worker processes, and each fit an estimator that itself used `n_jobs=-1` (RF/XGBoost via `n_jobs_model=-1`; **LightGBM via its all-cores default** when `n_jobs` is left unset). ~8×8 = ~64 threads contended for 8 cores → cache thrashing and context-switching: high CPU%, low useful throughput.

---

### Options Considered

Both options collapse to a single parallelism layer and eliminate oversubscription:

**Option A — outer owns the cores** (`n_jobs_cv=-1`, estimator `n_jobs=1`). Parallelise the CV/grid; each individual fit is serial.

**Option B — estimator owns the cores** (`n_jobs_cv=1`, estimator `n_jobs=-1`). Serial CV/grid; each fit uses all cores internally.

---

### Decision

**Option A — the outer CV/grid owns all cores; every estimator is single-threaded** (`n_jobs_model = 1`, applied to RF/XGBoost and now set explicitly on LightGBM, whose `None` default otherwise grabs all cores). Two secondary changes ship with it:

- **`oob_score=False` on RF.** Tuning selects on CV R² and eval reports Pearson r; `.oob_score_` is read nowhere, so computing it only added a redundant out-of-bag prediction pass to every one of the ~400 fits per `(endpoint, featureset)`.
- **The lone final refit in `model_validation` bumps `n_jobs=-1`** (guarded on the model exposing `n_jobs`). That fit runs after the CV, outside any parallel loop, so it cannot oversubscribe — it recovers full-core speed for the one place Option A would otherwise leave serial.

---

### Rationale — why Option A over Option B

1. **Three of the six models cannot self-parallelise.** SVR (libsvm), Lasso, and BayesianRidge expose no `n_jobs` (verified). Under Option B their entire grids (SVM 48 combos, Lasso 9) would run one fit at a time on a single core, 7 idle. Option A parallelises the CV/grid uniformly for *every* model, the single-threaded ones included. This is the decisive reason.
2. **Outer parallelism scales better even for the tree models.** `GridSearchCV` over `(combo, fold)` is embarrassingly parallel (independent full fits, near-linear speedup); estimator-internal `n_jobs` parallelises tree-building within one forest, with coordination overhead and sub-linear scaling. Small stages (e.g. XGBoost's 3-combo gamma stage) still get 5-fold outer parallelism.
3. Option B's only advantage is lower peak RAM (one model resident vs ~8). Peak here is ~2–3 GB — a non-issue.

`n_jobs` and `oob_score` never affect fitted values, only wall-clock and RAM — all three changes are **fidelity-neutral**.

---

### Grid kept full (fidelity)

The remaining cost is the grid's genuine fit count (RF: 80 combos × 5-fold = 400 fits per `(endpoint, featureset)`; ~4,800 across the 4×3 sweep). Decision: **keep the paper's full 80-combo grid** rather than pruning the heavy combos (`n_estimators=1000`, unbounded `max_depth`/`max_features`). After the parallelism fix the sweep is correctly compute-bound — a multi-hour overnight job with zero wasted cycles — and faithfulness to Fang et al. (2023) outweighs the runtime saving. Notebook `01.5` keeps `n_jobs_cv = -1`; no notebook code change was needed, since the models come from `get_paper_models()`, which now carries the fix.

---

### FCNN CV parallelism — serial (`n_jobs=1`)

The FCNN arm (`tune_fcnn_architecture` and the FCNN branch of `model_validation`) is a DeepChem/torch model, so CV-parallelizing it with `n_jobs=-1` both oversubscribes torch's own intra-op threads and risks deadlock / pickle failure under macOS `spawn` (the reason the MPNN branch already forces `n_jobs=1`). **Decision: FCNN uses `n_jobs=1` at all three notebook call sites** (§4.2 base, §4.3a tuning, §4.3b tuned); tree/linear models keep `n_jobs_cv=-1` so the outer CV still owns the cores. Torch parallelizes each individual fit internally, so serial folds are the right call, not a compromise.

As a complementary hedge for unattended overnight runs, `run_checkpointed_eval` now wraps each key's compute in try/except-log-continue (`continue_on_error=True`, default): a single FCNN/torch crash mid-run no longer aborts the whole batch — the failed key is logged, skipped, and retried on the next run (it is never checkpointed). A checkpoint-write failure still propagates (fail-fast on disk problems), and `Ctrl-C` still stops the run.

---

### Location

`src/hyperparams/hyperparams.py` (`n_jobs_model`, `param_base_RF`, `param_base_LGB`); `src/models/paper_models.py` (`model_validation` refit bump + corrected docstring; `run_checkpointed_eval` resilience guard); `tests/test_hyperparams.py` (guards estimators single-threaded + RF OOB off); `tests/test_models.py` (checkpoint resilience tests); `notebooks/01.5_adme_biogen_public_recreation.ipynb` (FCNN gated to `n_jobs=1` at the three §4.2/4.3 call sites).

---

### Update (2026-08-02) — Measured head-to-head; Option B stands (on wall-clock, not RAM)

After this ADR chose Option A, a RAM scare prompted reverting the code to **Option B** (`n_jobs_model=-1`, notebook `n_jobs_cv=1`) without updating this ADR. This session benchmarked both layouts head-to-head on the worst-case unit (`RLM | rdkit`, real `tune_paper_model` path) and **confirms Option B as correct for this project's tree-heavy grid** — though for a different reason than the revert assumed.

| Model | B (`n_jobs_model=-1`, cv=1) | A (`n_jobs_model=1`, cv=3) |
|-------|-----------------------------|----------------------------|
| RF (8 combos ×5) | **409 s** / 610 MB | 1038 s / 1324 MB |
| SVM (48 ×5) | 87 s / 461 MB | **35 s** / 703 MB |
| Lasso (9 ×5) | 8 s / 459 MB | **2.4 s** / 807 MB |
| **Total** | **504 s / 610 MB** | 1076 s / 1324 MB |

1. **B wins overall 2.1×.** RF dominates the grid, and forests parallelise *within* a fit far better than *across* folds — B's multi-core forests beat A's single-core ones ~2.5× on the heavy corner (`n_estimators=1000`, `max_features=None`). XGBoost/LightGBM self-parallelise identically. The paper grid is tree-heavy, so B is right. This makes **rationale point 2 above ("outer parallelism scales better even for the tree models") empirically false for the heavy RF corner.**
2. **A wins SVM/Lasso** (2.4× / 3.3×) exactly as this ADR predicted — they have no `n_jobs` — but they are cheap absolutely, so the ~60 s they save cannot offset RF's ~630 s loss.
3. **The RAM scare was a misdiagnosis.** Peak RSS across the whole loky process tree was 610 MB (B) / 1324 MB (A) — both trivial on the 17.2 GB Air. The ~98 GB seen earlier was *virtual/swap* from a stale overlapping `nbconvert` run + idle kernels + battery sleep (see LESSONS_LEARNED), **not** the parallelism layout. No layout here can produce 98 GB. Point 3 above ("peak here is ~2–3 GB — a non-issue") was the *correct* call; the revert to B was over-cautious about RAM but happens to be right on wall-clock.

**Net: Option B (current code) stands, validated on wall-clock.** Revisit only if a future workload becomes SVM/Lasso/BayesianRidge-heavy. Harness + raw logs: `benchmarks/bench_parallelism.py`, `benchmarks/result_parallelism_{A,B}.txt`.

---

### Update (2026-08-03) — Single source of truth for both `n_jobs` knobs

Previously `n_jobs_model=-1` lived in `src/hyperparams/hyperparams.py` (baked into `param_base_*` at import) while `n_jobs_cv=1` was redefined in the notebook — two files that could silently disagree and re-trigger the oversubscription trap. **Both knobs now live in `hyperparams.py`** (`n_jobs_cv` added next to `n_jobs_model`, exported via `__init__.py`); the notebook **imports** them in §0 instead of redefining, so the Option-B invariant (`model=-1` ⇒ `cv=1`) is enforced in one place. No behaviour change — same values, single source. (Notebook-only was not chosen: `param_base_*` need `n_jobs_model` at import time.)

---

**Last Updated**: 2026-08-03

---

## ADR-009 — ChemProp 1.6.1 Has No MPS (GPU) Path; Pin Its Implicit Training Defaults

**Date**: 2026-08-02
**Status**: Decided
**Decider**: Zarif

---

### Context

"Training the DNNs on a MacBook Air (M4, no discrete GPU) is slow" prompted checking whether the M4's integrated GPU (via PyTorch's MPS backend) could accelerate the MPNN (ChemProp) or FCNN (DeepChem).

---

### Findings

1. **ChemProp 1.6.1 cannot use the M4 GPU at all.** Its `TrainArgs.device` property returns `torch.device('cpu')` unless `cuda`, else `torch.device('cuda', gpu)` — there is **no MPS branch** (verified by reading the installed source). So the MPNN runs on CPU here regardless of `torch.backends.mps.is_available()` being True. Reaching MPS would require patching device selection or upgrading — and 1.6.x → 2.x is a full API rewrite that breaks this project's CLI-args wrapper, while torch 2.0.1's MPS coverage of the scatter/gather ops message-passing needs is incomplete.
2. **FCNN can reach MPS, but it is slower.** DeepChem's `MultitaskRegressor` forwards `device` to `TorchModel`; measured on `RLM | rdkit`, 50 epochs: **CPU 1.8 s vs MPS 6.4 s (MPS 3.6× slower)**. The net is too small — a full fit is under 2 s on CPU — so GPU launch/transfer overhead dwarfs the compute. Predictions agree across devices.

**Conclusion: no DNN in this project benefits from the M4 GPU.** The perceived slowness was process hygiene + battery sleep (see ADR-008 update / LESSONS_LEARNED) and, for the tree models, the `n_jobs` layout — not the missing GPU.

---

### Decision

- **Do not pursue MPS/GPU for the DNNs.** This holds *independently* of any speedup tactic: MPS is blocked for the MPNN by ChemProp 1.6.1's missing device path, and measured 3.6× *slower* for the FCNN because that net is tiny — neither fact depends on trial count or early stopping. The project is (deliberately, for now) **keeping full hyperopt trials and no MPNN early stopping**, so MPNN training is genuinely expensive; the realistic escalation if its wall-clock becomes a blocker is **cloud CUDA (Colab/Kaggle)**, not local MPS. (A future ChemProp≥2 + torch≥2.1 upgrade *might* let the larger MPNN graph compute benefit from MPS — untested, and gated behind the risky upgrade we are avoiding.)
- **Pin ChemProp's implicit training-schedule defaults explicitly** in `src/models/mpnn.py` (`_PINNED_CHEMPROP_DEFAULTS` + an explicit `--ffn_hidden_size`), wired into **both** `fit()` and `tune_mpnn_hyperopt()` so trials and final training share one schedule. Pinned values — `batch_size=50`, `init_lr/max_lr/final_lr = 1e-4/1e-3/1e-4`, `warmup_epochs=2.0`, `activation=ReLU`, `aggregation=mean`, `aggregation_norm=100`, `ffn_hidden_size=hidden_size` — were each **verified equal to 1.6.1's defaults on 2026-08-02**, so this is **fidelity-neutral today**. Its sole purpose is insurance: a future ChemProp/dependency change can no longer silently alter MPNN behaviour. (`bias`, default False, is a `store_true` flag with no CLI way to force it False, so it remains implicit.) The tuned architecture set — `hidden_size/depth/dropout/ffn_num_layers`, the "S14" config — was already pinned.

---

### Rationale

The four architecture hyperparameters were pinned (they define MPNN S14) but the entire training schedule rode on ChemProp's implicit defaults — a silent reproducibility hole. Pinning them now, while they still equal the defaults, costs nothing and removes the exact risk that made a version upgrade unsafe. Combined with the MPS finding, this settles both "can the GPU help" (no) and "is upgrading ChemProp safe" (only after these are pinned, which they now are).

---

### Location

`src/models/mpnn.py` (`_PINNED_CHEMPROP_DEFAULTS`, fit + hyperopt wiring, explicit `--ffn_hidden_size`); benchmark harnesses + raw logs in `benchmarks/` (`bench_parallelism.py`, `bench_fcnn_device.py`, `result_*.txt`).

---

**Last Updated**: 2026-08-02

---

---

## ADR-010 — Per-Group (Not Pooled) Normality Check for the Section 5.5 ANOVA

**Date**: 2026-08-03
**Status**: Decided
**Decider**: Zarif

---

### Context

The Section 5.5 per-endpoint `AnovaRM` assumes normality of the residuals. Normality was
diagnosed in the notebook with a Shapiro-Wilk test + Q-Q plot computed **per (endpoint, model)
group** on the raw 15 CV Pearson-r scores, rather than on the pooled ANOVA residuals (the more
conventional single-Q-Q-per-endpoint diagnostic).

---

### Decision

Keep the per-group diagnostic. It is valid, not a substitute error for pooling.

> Normality was checked per-group rather than on pooled residuals. Within a group, residuals
> differ from the raw Pearson-r values only by a constant (the group mean), so the shape — and
> hence the Q-Q/skew/kurtosis — is identical; the per-group view is simply a finer diagnostic
> that also reveals which model deviates.

---

### Rationale

Within a single group the residual is `r_i − mean(group)`, i.e. the raw values shifted by a
constant. A constant shift leaves skew, excess kurtosis, and the Q-Q pattern unchanged, so
testing the per-group raw scores is equivalent *in shape* to testing per-group residuals. The
per-group view is strictly more informative than the pooled one because it localises *which*
model's distribution deviates — here it flagged HLM/MPNN3 (skew −1.16) and MDR1/RF (skew +1.56,
excess kurtosis +2.25) individually, which a single pooled Q-Q would have blurred together.
With only 15 folds per group, both Shapiro-Wilk (low power at n=15) and the skew/kurtosis
estimates are noisy, so the numbers are read as indicative, not definitive.

---

### Consequence

RM-ANOVA is robust to mild non-normality under this balanced design, and the omnibus F values on
the strong endpoints are large, so the ANOVA conclusions stand. The one localised caveat is
**Tukey HSD pairwise rows involving RF at MDR1**: RF's MDR1 group is right-skewed with a heavy
tail (an outlier fold ≈0.76) that inflates its variance, straining Tukey's normality + equal-
variance assumptions for those specific comparisons — noted in the notebook. HLM/MPNN3 is not
pursued (that data is being migrated). No non-parametric cross-check (Friedman/Nemenyi) was added:
SOL and RLM satisfied normality, so their mismatch against the paper is a reproduction question,
not an assumption-validity one, and the deviating groups sit on endpoints whose omnibus verdicts
are unaffected.

---

*Add new ADRs above this line, numbered sequentially.*

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

The MPNN2 tuned arm uses `metric='mae'` in ChemProp's early stopping for the same reason (see `_run_mpnn2` in `03_adme_experiments.ipynb`); the MPNN2 baseline arm uses ChemProp's default `metric='rmse'`. Note that in ChemProp 1.6.1 `--metric` controls the early stopping criterion only — the training loss is hardcoded to MSE for regression regardless of this flag. So MPNN2 trains with MSE in both arms.

---

**Last Updated**: 2026-07-21

*Add new ADRs above this line, numbered sequentially.*

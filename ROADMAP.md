# Roadmap - Strategic Vision

## Breadcrumbs

- **New to the project?** → [CLAUDE.md](CLAUDE.md) for setup and overview
- **Current work?** → [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Pipeline handoffs?** → [SYNCHRONIZATIONS.md](SYNCHRONIZATIONS.md)

---

## Purpose

**ROADMAP.md** is the strategic compass for the 6-week project:
- **Where are we going?** (vision and research goals)
- **Why does it matter?** (scientific rationale)
- **What are we building, and in what order?** (phased plan)

This is NOT a task list — see [PROJECT_PLAN.md](PROJECT_PLAN.md) for current sprint detail.

---

## Vision

**UNIQ+ 6 week research project** aims to quantify how dataset size and label noise affect ML model performance for molecular property prediction (QSAR), using two+ open-source drug discovery datasets. Findings should be reproducible and documented well enough to support a methods section if taken to publication.

**Success looks like**:
- Learning curves showing how R², RMSE, MAE, Spearman ρ, and CCC degrade as training set size decreases — for each endpoint and model
- Noise experiments showing the threshold at which label noise meaningfully degrades model performance
- A clean, reproducible notebook pipeline with reusable `src/` helpers that a reader could run independently
- Clear documentation of split strategy decisions and their effect on reported performance

---

## 6-Week Phased Plan

### Phase 1 — Weeks 1–2: EDA + Baseline Models (ADME)

**Goal**: Understand the ADME dataset and establish a working baseline pipeline.

**Initiatives**:
1. **Exploratory data analysis** — distributions, SMILES validity, missing values, endpoint correlations
2. **Data cleaning** — strategy decided post-EDA (see [SYNC-002](SYNCHRONIZATIONS.md))
3. **Featurization** — Morgan fingerprints (ECFP4, 2048 bits) as primary; RDKit 2D descriptors as secondary
4. **Baseline models** — MeanPredictor (dummy baseline), Ridge (interpretable baseline), BayesianRidge (Bayesian linear baseline), RF, XGBoost, LightGBM on all 6 ADME endpoints; random train/test split
5. **Evaluation** — R², RMSE, MAE, Spearman ρ, CCC; predicted vs actual plots per endpoint

**Exit criteria**: Baseline performance documented for all 6 ADME endpoints across 4 models.

---

### Phase 2 — Week 3: PDE10A Dataset + Split Strategy Comparison

**Goal**: Establish a complete baseline picture across both datasets before designing experiments.

**Initiatives**:
1. **EDA on PDE10A** — pIC50 distribution, compound diversity, temporal coverage across splits
2. **Baseline models on PDE10A** — same 5-model set, all 7 split strategies (temporal 2011–2013, chemotype-based, random)
3. **Split strategy comparison** — how much does the choice of split inflate or deflate reported R²/RMSE?

**Rationale for reordering**: Having baselines for both datasets before designing experiments gives supervisors a complete picture. Learning curve and noise injection decisions (fractions, noise types, which datasets) are better made once PDE10A's data distribution, effective N per split, and baseline R² are known.

**Exit criteria**: Performance comparison across 7 split strategies documented; cross-dataset comparison with ADME baselines noted.

---

### Phase 3 — Baseline Tuning (Clean Data Reference)

**Goal**: Tune models once on clean, full training data to establish a reference point and validate the tuning pipeline before running experiments.

**Initiatives**:
1. **Tune LightGBM** — `RandomizedSearchCV` (n_iter=50, cv=5) over `n_estimators`, `learning_rate`, `num_leaves`, `min_child_samples`, `subsample`, `colsample_bytree` for 4 modelling endpoints (HLM, MDR1, SOL, RLM)
2. **Tune RandomForest** — `RandomizedSearchCV` (n_iter=50, cv=5) over `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features` for 4 endpoints
3. **Tune MPNN2** — Fixed architecture (`hidden_size=300, depth=3`, ChemProp defaults) with early stopping (`--epochs 50`). 4 endpoints.
4. **Compare** — Report tuned vs baseline R², RMSE, MAE, Spearman ρ, CCC to quantify tuning benefit on clean data

**Module**: `src/tuning/` — see [src/tuning/CLAUDE.md](src/tuning/CLAUDE.md)

**Exit criteria**: Tuned R² documented for LightGBM, RF, and MPNN2 on 4 endpoints; tuning pipeline validated and ready for experiment loop.

---

### Phase 4 — Learning Curves (Quantity Axis)

**Goal**: Quantify how model performance degrades as training set size decreases, at zero noise (σ=0). Compare baseline (untuned) vs tuned models.

**Two experimental arms**:
- **Baseline arm**: Default-hyperparameter LightGBM, RF, BayesianRidge — train on subsample, evaluate
- **Tuned arm**: Re-tune LightGBM and RF via `RandomizedSearchCV` on each subsample, then evaluate. Shows whether tuning helps (or hurts) at small N.

**Initiatives**:
1. **Subsample training sets** — fractions ∈ {0.05, 0.10, 0.25, 0.50, 0.75, 1.0} of each endpoint's training set; 10 random seeds per fraction for variance estimation
2. **Baseline arm** — fit default models on subsample, evaluate on fixed clean test set
3. **Tuned arm** — re-tune on each subsample (CV folds drawn from subsample), evaluate on fixed clean test set
4. **Record per run** — R², RMSE, MAE, Spearman ρ, CCC per (model, endpoint, fraction, seed, arm)
5. **Aggregate and plot** — mean ± std learning curves per model per arm; identify performance plateau per endpoint; compare baseline vs tuned gap across N

**Models**: LightGBM, RandomForest, MPNN2, BayesianRidge (baseline only — no tuning for BayesianRidge)

**Exit criteria**: Learning curves complete for 4 modelling endpoints (HLM, MDR1, SOL, RLM) for both arms; baseline vs tuned comparison documented.

---

### Phase 5 — Noise Injection (Noise Axis)

**Goal**: Quantify how model performance degrades as label noise increases, at full N. Compare baseline vs tuned models under noise.

**Noise types** (following the Landrum & Riniker error taxonomy):

1. **Gaussian (intra-assay variability)** — `y_noisy = y + N(0, σ)` where σ ∈ {0, 0.1, 0.3, 0.5, 1.0} × endpoint_std. Models normal experimental noise: replicate-to-replicate variation within the same assay protocol. Physically motivated for log-scale ADME endpoints.
2. **Systematic bias (inter-assay differences)** — `y_biased = y + c` where c ∈ {0, 0.1, 0.3, 0.5, 1.0} × endpoint_std. Models lab-to-lab or protocol-to-protocol offsets (different readout technology, substrate concentrations). Applied to a random fraction of training labels (simulating data merged from multiple sources).
3. **Gross errors (annotation errors)** — Replace k% of training labels with values drawn uniformly from the endpoint's range; k ∈ {1, 5, 10, 20}. Models compound misidentification, data entry errors, or database merge artifacts. Qualitatively different from smooth perturbations — tests model robustness to catastrophic label corruption.

**Two experimental arms**:
- **Baseline arm**: Default-hyperparameter models trained on noisy data, evaluate on clean test
- **Tuned arm**: Re-tune on noisy data (CV folds inherit noise — realistic regime), evaluate on clean test

**Initiatives**:
1. **Inject noise into training labels only** — test set always clean
2. **10 seeds per noise level** — for variance estimation
3. **Both arms** — baseline and tuned, evaluated on fixed clean test set
4. **Record per run** — R², RMSE, MAE, Spearman ρ, CCC per (model, endpoint, noise_type, noise_level, seed, arm)
5. **Plot** — noise degradation curves per model per arm per noise type; identify threshold where performance meaningfully degrades
6. **Compare** — does tuning buy noise resilience? Do tree models tolerate gross errors better than linear models?

**Models**: LightGBM, RandomForest, MPNN2, BayesianRidge (baseline only)

**Exit criteria**: Noise curves complete for both arms on 4 modelling endpoints across all 3 noise types; degradation thresholds documented.

---

### Phase 5b — Validation Set Quality Sub-Experiment

**Goal**: Determine whether a clean validation set improves hyperparameter selection under noise — and how important this is for real-world applications.

**Design**: At 3 representative training sizes (full N, 25%, 5%), compare two tuning regimes under each noise level:
- **Arm A (realistic)**: Noisy validation — `RandomizedSearchCV` with CV folds drawn from noisy training data. This is what a practitioner would actually do.
- **Arm B (ideal)**: Clean validation — hold out 15–20% of training data as a clean validation set before injecting noise. Tune by fitting on noisy remainder, scoring on clean holdout.

**Initiatives**:
1. **Run at 3 sizes × noise levels** — not the full grid, just enough to see the interaction between N, σ, and validation quality
2. **Compare selected hyperparameters** — do noisy CV and clean validation select different params? (e.g., more regularisation under clean val?)
3. **Compare test-set performance** — how much does clean validation improve final R² on the clean test set?
4. **Interpret** — if Δ is large at high noise, clean validation sets are worth curating in practice; if small, noisy CV is sufficient

**Exit criteria**: Comparison table at 3 sizes × noise levels showing Δ(R²) between arms A and B; practical recommendation documented.

---

### Phase 6 — 2D Experiment Grid + Writeup

**Goal**: Map the joint surface performance = f(N, σ); write up findings.

**Initiatives**:
1. **2D grid** — all combinations of N × noise_level for each noise type; both baseline and tuned arms; 5 seeds per cell (reduced for cost)
2. **Surface plots** — R² as a function of (N, noise_level) per model per noise type per arm (primary surface metric); MAE, Spearman ρ, and CCC reported in supplementary result tables
3. **Cross-cutting analysis** — does noise tolerance depend on dataset size? Does model rank change across the surface? Does the tuning benefit shrink or grow with noise/small N? Do gross errors interact differently with data quantity than Gaussian noise?
4. **Writeup** — clean notebooks, figures, summary of key results; interpret through PrO/misspecification lens

**Models**: LightGBM, RandomForest, MPNN2, BayesianRidge (baseline only)

**Exit criteria**: 2D surface computed and plotted for at least HLM and MDR1 across all 3 noise types for both arms; findings summarised in a results notebook.

---

### Previously: Phase 3 (original) — Experiments + Writeup

*Superseded by the above four-phase breakdown (Phases 3–6). The original scope (learning curves + noise injection) is preserved but now split into discrete phases with explicit exit criteria.*

---

## Key Strategic Decisions

### Featurization: ECFP4 Morgan Fingerprints (Confirmed)

**Decision**: ECFP4 Morgan fingerprints (radius=2, 2048 bits) are the primary featurization. RDKit 2D descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds) are implemented as a secondary/swap option. Both are implemented in `src/features.py`; swapping is trivial.

**Rationale**: Both are valid for QSAR. RDKit 2D descriptors are interpretable and well-supported; Morgan fingerprints (ECFP4) are the literature standard and require no fitting step. Supervisors confirmed ECFP4 as primary.

### Metrics: R², RMSE, MAE, Spearman ρ, CCC throughout (MSE dropped)

**Decision**: Report R², RMSE, MAE, Spearman ρ, and CCC for every model evaluation. MSE is dropped.

**Rationale**:
- **R²**: Scale-independent, allows cross-endpoint comparison, the standard headline metric in QSAR literature. Primary surface metric for Phase 6 plots.
- **RMSE**: Interpretable in target units, widely expected. Kept alongside R².
- **MSE**: Dropped — it is RMSE² and adds no interpretive value beyond RMSE.
- **MAE** (added): Does not square errors, so it is more robust to outliers than RMSE. Important for noise experiments where gross error injection (k% random label corruption) creates extreme values that would disproportionately inflate RMSE and obscure the typical model error.
- **Spearman ρ** (added): Rank-based and scale-free, making it directly comparable across all four endpoints (HLM, MDR1, SOL, RLM) without normalisation — unlike RMSE, which is in target units and cannot be compared across endpoints. Also robust to outliers: when gross error injection produces wild predictions on a handful of test compounds, Spearman ρ ignores the magnitude of those errors and reflects whether the model still captures the underlying trend across the test set.
- **CCC — Concordance Correlation Coefficient** (added): Standard in QSAR evaluation literature. Unlike R², CCC penalises both scatter *and* systematic bias simultaneously — a model that predicts a perfectly correlated but shifted output scores high R² but low CCC. Especially diagnostic for the systematic bias noise type (Phase 5), where models trained on shifted labels may produce biased predictions on the clean test set.

### Predictively Oriented Posteriors (PrO): referenced, not implemented

**Decision**: PrO posteriors (Fong & Holmes, arXiv:2510.01915) are incorporated as a theoretical framework reference, not a full experiment. `BayesianRidge` is added as a fourth baseline in Phase 1 as a lightweight Bayesian comparison point. Full PrO implementation is deferred to future work.

**Why PrO is genuinely relevant**: QSAR models are inherently misspecified (descriptors are coarse summaries of complex biology) — exactly the regime PrO is designed for. PrO's core property, that posteriors don't collapse under persistent misspecification, maps directly onto two of our research questions: (1) learning curves flattening as N grows reflects a misspecification ceiling, not just a data ceiling; (2) label noise injection artificially worsens misspecification, and PrO's "irreducible uncertainty" is a principled diagnostic for this. PrO also predicts that chemotype-based splits would produce higher, less reducible uncertainty than random splits — relevant to Phase 3.

**Why full implementation is not suitable now**: No Python package exists (October 2025 paper); correct implementation requires coding the PrO update rule from scratch. Computational cost would be prohibitive across the full experiment grid (learning curve fractions × noise levels × 6 endpoints × 2 datasets). Adding this would pivot the project from empirical data-centric research toward Bayesian methodology research — a different paper.

**What we do instead**: BayesianRidge as a cheap Bayesian baseline; Phase 4 writeup interprets noise and data-quantity results through the PrO lens (performance degradation as entry into a misspecification regime, not just RMSE increase). This adds theoretical depth without new experiments.

**Future work**: If extended to publication, implement PrO for a linear QSAR model and use PrO uncertainty spread as a noise diagnostic — a novel contribution to both Bayesian ML and computational drug discovery. See [DECISIONS.md](DECISIONS.md) ADR-001 for full reasoning.

**Review when**: If project extends beyond 6 weeks.

### Deep learning models (ChemProp / DeepChem / Tx-Gemma): pending

**Decision**: TBD — to be decided after Phase 1 baselines are established and time remaining is assessed. Tx-Gemma is a candidate but dataset size suitability for fine-tuning is unknown; Zarif to investigate. ChemProp/DeepChem are lighter-weight alternatives.

**Review when**: End of Phase 2 (Week 3).

---

**Last Updated**: 2026-07-20
**Next Review**: End of Phase 2 (Week 3) — supervisor review to confirm experiment scope

**Related**: [PROJECT_PLAN.md](PROJECT_PLAN.md) · [SYNCHRONIZATIONS.md](SYNCHRONIZATIONS.md) · [CLAUDE.md](CLAUDE.md) · [CHANGELOG.md](CHANGELOG.md)

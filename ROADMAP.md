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

**UNIQ+** aims to quantify how dataset size and label noise affect ML model performance for molecular property prediction (QSAR), using two open-source drug discovery datasets. Findings should be reproducible and documented well enough to support a methods section if taken to publication.

**Success looks like**:
- Learning curves showing how R², RMSE, and MSE degrade as training set size decreases — for each endpoint and model
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
4. **Baseline models** — Linear Regression (interpretable baseline), BayesianRidge (Bayesian linear baseline), RF, XGBoost, LightGBM on all 6 ADME endpoints; random train/test split
5. **Evaluation** — R², RMSE, MSE; predicted vs actual plots per endpoint

**Exit criteria**: Baseline performance documented for all 6 ADME endpoints across 4 models.

---

### Phase 2 — Week 3: Data Quantity Experiments (ADME)

**Goal**: Quantify the effect of training set size on model performance.

**Initiatives**:
1. **Learning curves** — subsample training set at increasing fractions; evaluate on fixed test set
2. **Analysis** — identify at what training size performance plateaus or degrades significantly per endpoint

**Exit criteria**: Learning curve plots for each ADME endpoint × model combination.

---

### Phase 3 — Week 4: PDE10A Dataset + Split Strategy Comparison

**Goal**: Introduce the PDE10A dataset and investigate how split strategy affects reported performance.

**Initiatives**:
1. **EDA on PDE10A** — pIC50 distribution, compound diversity, temporal coverage
2. **Baseline models on PDE10A** — same model set, all 7 split strategies (temporal 2011–2013, chemotype-based, random)
3. **Split strategy comparison** — how much does the choice of split inflate or deflate reported R²/RMSE?

**Exit criteria**: Performance comparison across 7 split strategies documented; cross-dataset comparison with ADME baselines noted.

---

### Phase 4 — Weeks 5–6: Noise Injection + Analysis + Writeup

**Goal**: Quantify the effect of label noise on model performance; consolidate findings.

**Initiatives**:
1. **Noise injection** — Gaussian noise and label shuffle at increasing fractions on both datasets
2. **Robustness analysis** — at what noise level does each model break down? Are some models more noise-tolerant?
3. **Final analysis** — cross-cutting findings: does dataset size interact with noise tolerance?
4. **Writeup** — clean notebooks, figures, summary of key results

**Exit criteria**: Noise experiments complete on at least ADME; findings summarised in a results notebook.

---

## Key Strategic Decisions

### Featurization: ECFP4 Morgan Fingerprints (Confirmed)

**Decision**: ECFP4 Morgan fingerprints (radius=2, 2048 bits) are the primary featurization. RDKit 2D descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds) are implemented as a secondary/swap option. Both are implemented in `src/features.py`; swapping is trivial.

**Rationale**: Both are valid for QSAR. RDKit 2D descriptors are interpretable and well-supported; Morgan fingerprints (ECFP4) are the literature standard and require no fitting step. Supervisors confirmed ECFP4 as primary.

### Metrics: R², RMSE, MSE throughout

**Decision**: Report all three for every model evaluation.

**Rationale**: R² is scale-independent (allows cross-endpoint comparison); RMSE is interpretable in target units; MSE is required to compute RMSE and is reported for completeness.

### Predictively Oriented Posteriors (PrO): referenced, not implemented

**Decision**: PrO posteriors (Fong & Holmes, arXiv:2510.01915) are incorporated as a theoretical framework reference, not a full experiment. `BayesianRidge` is added as a fourth baseline in Phase 1 as a lightweight Bayesian comparison point. Full PrO implementation is deferred to future work.

**Why PrO is genuinely relevant**: QSAR models are inherently misspecified (descriptors are coarse summaries of complex biology) — exactly the regime PrO is designed for. PrO's core property, that posteriors don't collapse under persistent misspecification, maps directly onto two of our research questions: (1) learning curves flattening as N grows reflects a misspecification ceiling, not just a data ceiling; (2) label noise injection artificially worsens misspecification, and PrO's "irreducible uncertainty" is a principled diagnostic for this. PrO also predicts that chemotype-based splits would produce higher, less reducible uncertainty than random splits — relevant to Phase 3.

**Why full implementation is not suitable now**: No Python package exists (October 2025 paper); correct implementation requires coding the PrO update rule from scratch. Computational cost would be prohibitive across the full experiment grid (learning curve fractions × noise levels × 6 endpoints × 2 datasets). Adding this would pivot the project from empirical data-centric research toward Bayesian methodology research — a different paper.

**What we do instead**: BayesianRidge as a cheap Bayesian baseline; Phase 4 writeup interprets noise and data-quantity results through the PrO lens (performance degradation as entry into a misspecification regime, not just RMSE increase). This adds theoretical depth without new experiments.

**Future work**: If extended to publication, implement PrO for a linear QSAR model and use PrO uncertainty spread as a noise diagnostic — a novel contribution to both Bayesian ML and computational drug discovery. See [DECISIONS.md](DECISIONS.md) ADR-001 for full reasoning.

**Review when**: If project extends beyond 6 weeks or targets publication.

### Deep learning models (ChemProp / DeepChem / Tx-Gemma): pending

**Decision**: TBD — to be decided after Phase 1 baselines are established and time remaining is assessed. Tx-Gemma is a candidate but dataset size suitability for fine-tuning is unknown; Zarif to investigate. ChemProp/DeepChem are lighter-weight alternatives.

**Review when**: End of Phase 2 (Week 3).

---

**Last Updated**: 2026-07-10
**Next Review**: End of Phase 1 (Week 2)

**Related**: [PROJECT_PLAN.md](PROJECT_PLAN.md) · [SYNCHRONIZATIONS.md](SYNCHRONIZATIONS.md) · [CLAUDE.md](CLAUDE.md) · [CHANGELOG.md](CHANGELOG.md)

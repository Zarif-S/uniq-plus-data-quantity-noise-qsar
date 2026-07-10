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

*Add new ADRs above this line, numbered sequentially.*

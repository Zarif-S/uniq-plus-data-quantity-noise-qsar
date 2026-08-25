# Lessons Learned - UNIQ+

Captured process and technical lessons as they arise. Referenced during project retrospectives and when setting up future projects.

---

## Process

### Doc setup order matters

**Lesson**: When setting up the agentic coding framework, populate docs in this order:
1. `ROADMAP.md` — establish the vision and 6-week arc first
2. `SYNCHRONIZATIONS.md` — map pipeline flows against that vision
3. `PROJECT_PLAN.md` — define current sprint/phase in context of both above

**Why**: Starting with SYNCHRONIZATIONS before ROADMAP meant defining pipeline handoffs without a clear picture of the overall goals and phasing. The roadmap provides the context that makes sync decisions meaningful.

---

## Technical

### Skill files must physically exist before being listed as installed

**Lesson**: When documenting skills in `SKILLS-SOURCES.md` (or equivalent), only list a skill as "installed" if the corresponding `.md` file is physically present in `.claude/commands/`. It is easy to list a skill in a table and assume it was installed, but if the file was never copied the `/skill` command silently fails with no useful error.

**Concrete case**: RDKit skill was listed as installed in `SKILLS-SOURCES.md` but the file `.claude/commands/rdkit.md` may never have been downloaded from `https://github.com/K-Dense-AI/scientific-agent-skills`. Manual verification required.

**Fix for this project**: Zarif to manually download each listed skill's `SKILL.md` and `cp` it into `.claude/commands/<skill-name>.md`, then verify with `ls .claude/commands/`.

**Portfolio-level action (for future projects)**: Add a verification step to the project setup checklist — after populating `SKILLS-SOURCES.md`, run `ls .claude/commands/` and confirm every listed skill has a corresponding file. Consider adding a one-liner to the setup docs:
```bash
# Verify all listed skills are physically installed
ls .claude/commands/*.md
```
Also update the `agentic-coding-framework` CLAUDE.md template to include: "⚠ Verify skill files exist before marking as installed."

### Use FCFP4, not ECFP4, for this paper recreation

**Lesson**: When replicating Fang et al. (2023), always use `useFeatures=True` (FCFP4), not `useFeatures=False` (ECFP4). The paper uses FCFP4 throughout — fingerprints, similarity calculations, and featurization. ECFP4 encodes atom identity; FCFP4 encodes pharmacophoric feature class (H-bond donor/acceptor, charge, aromatic, etc.), which is more appropriate for ADME modelling where functional group character matters more than exact atom type.

**Concrete case**: The paper text says "radius 4 (FCFP4)" — follow the code (`radius=2, useFeatures=True`), not the text. The text confuses radius with diameter.

---

### Claude code-gen tics to watch for in review

**Lesson**: Habits Claude defaults to that don't match this project's conventions or the user's own style — worth a quick eyeball pass, not automatic fixes.
- Semicolon-chained statements (`ax.set_title(x); ax.set_xlabel(y)`, `plt.tight_layout(); plt.show()`) — CLAUDE.md bans this; one statement per line
- Docstrings that grow past one line (rationale/caveats baked in) — CLAUDE.md wants one-line docstrings only
- Comments restating what the code does instead of why
- Defensive code (None-checks, try/except, fallback defaults) for cases that can't actually happen given call sites
- Reaching for a class/​`**kwargs` flexibility where a plain function/fixed signature would do

---

### Use Sørensen-Dice similarity, not Tanimoto, for this dataset

**Lesson**: For the Fang et al. (2023) paper recreation, use `DataStructs.BulkDiceSimilarity` (Sørensen-Dice), not Tanimoto. The paper explicitly states Sørensen-Dice in the methods section, and the numbers confirm it: Tanimoto gives mean=0.167 ± 0.059; Sørensen-Dice gives mean=0.282 ± 0.083, matching the paper's reported 0.28 ± 0.08 exactly. Tanimoto is the RDKit default, making it an easy mistake to reach for.

---

### §5.7 Table 2 won't numerically match Fang et al.'s Table 2 — three real, checked causes, none of which threaten the paper's qualitative claims

**Lesson**: When a recreation's numbers don't land on the original paper's published values, resist assuming your own pipeline is wrong or that the paper's claims are undermined — trace each candidate cause individually against the paper's actual public code (`ADME_ML_public.py`, Computational-ADME repo) before concluding either way. Investigated 2026-08-19–24; three causes confirmed, one theory tested and discarded.

**Confirmed causes** (see `DECISIONS.md` ADR-007 for full detail):
1. **RF/LightGBM unseeded in the paper's own script** — `RandomForestRegressor(...)` and `lgb.LGBMRegressor(...)` are instantiated with no `random_state`/`seed` at all (our `src/models/paper_models.py` passes one explicitly). MPNN's ChemProp invocation appears to have the same gap. This parallels the FCNN `seed=5758` bug already logged (wrong kwarg name, silently dropped by DeepChem 2.1.0) — different mechanism (omission vs. typo), same effect: the paper's own published numbers are one non-reproducible draw, not a fixed target.
2. **Dedup-key mismatch** — our loader does `drop_duplicates('can_smi')` post-standardization (merges two different vendor IDs that standardize to the same structure); the paper's script dedupes via a `dict` keyed on `molName`, which only collapses same-named rows and never checks structural identity across different IDs. Produces small compound-count deltas (e.g. HLM 3086 vs. published 3087) that are NOT something the paper's script would also produce — the earlier assumption that "the paper would have hit the same loss" was wrong and has been corrected in `DECISIONS.md`.
3. **Single-draw split variance, not a seeding bug** — when comparing CV_r vs. test_r across all 4 endpoints (HLM/MDR1/SOL/RLM) × both sources (paper's Table 2 vs. ours), the paper's HLM column was the one outlier cell (CV_r beats test_r by +0.01 to +0.05 across all 4 models, unlike every other endpoint in both tables). The split (`shuffle(42)` + `train_test_split(random_state=84)`) *is* fully seeded and deterministic — but each endpoint has a different compound list, so a fixed seed still produces an independent one-off partition per endpoint. One random 80/20 draw (vs. the 15-fold CV mean) is expected to occasionally land on an easier/harder-than-average test slice purely by chance — no code fix would eliminate this, it's inherent to taking only one split per endpoint.

**Theory tested and discarded**: initially suspected our shared cross-endpoint `df_sdf` union (built for PPB/ChEMBL augmentation reuse) put molecules into `shuffle(42)` in a different order than the paper's per-endpoint processing, and that this structural difference explained the mismatch. The paper repo's `ML/` folder does contain separate per-endpoint SDFs (`ADME_HLM.sdf`, `ADME_MDR1_ER.sdf`, etc.), which reopens this as *possible*, but no evidence was found strong enough to confirm it drives the observed pattern — the split-variance explanation above fits the data better and needed no unverified assumption about their internal file structure.

**Why it doesn't matter for the write-up**: every one of the paper's qualitative claims (non-RF > RF, hybrid features > single representations, MPNN2/FCNN best-in-class, tuning marginal) is a *within-split, relative* comparison — models are ranked against each other on the same partition. Both cause #1 and #3 apply near-uniformly across models evaluated on the same split, so they wash out of relative comparisons even though they show up clearly in absolute value comparisons against the published table. Confirmed the user's own recreation reproduces the same relative ordering.

---

**Last Updated**: 2026-08-24

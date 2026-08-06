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

**Last Updated**: 2026-07-22

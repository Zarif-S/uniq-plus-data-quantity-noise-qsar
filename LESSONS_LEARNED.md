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

---

**Last Updated**: 2026-07-10

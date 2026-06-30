# Plan Feature

Turn a feature description into a concrete documentation plan: a PROJECT_PLAN.md entry, plus a triage of every other doc that needs updating.

## Steps

1. **Understand the feature** — If the user has described the feature in natural language, use that. Otherwise ask in a single message:
   - What does the feature do? (user-facing description)
   - Which concept(s) does it touch or introduce?
   - Is this new functionality, a change to existing behavior, or a fix?
   - Does it have any known dependencies or blockers?

2. **Read project state** — Before generating anything, read:
   - `PROJECT_PLAN.md` — understand current focus, active Now/Next/Later items, and active blockers
   - `SYNCHRONIZATIONS.md` — check whether the feature introduces new cross-concept flows
   - Root `CLAUDE.md` — check which concept CLAUDE.md files exist (from the navigation table)
   - `ROADMAP.md` — identify which strategic initiative or milestone this feature belongs to

   If any of these files don't exist, note which ones are missing but continue with what's available.

3. **Classify the feature** — Determine where it belongs in PROJECT_PLAN.md:
   - **Now**: user says it's actively being worked on, or it unblocks something currently in Now
   - **Next**: user intends to start it soon, or it depends on something in Now
   - **Later**: exploratory, speculative, or has no clear start date

4. **Triage doc updates** — For each document below, decide: `needs update`, `no change needed`, or `new file required`. Show the triage as a table before writing anything.

   | Document | Decision | Reason |
   |----------|----------|--------|
   | `PROJECT_PLAN.md` | needs update | Add feature to Now/Next/Later |
   | `SYNCHRONIZATIONS.md` | needs update / no change | New cross-concept flow? |
   | `[concept]/CLAUDE.md` | needs update / no change | New state, actions, or invariants? |
   | `ROADMAP.md` | needs update / no change | New initiative or milestone? |
   | `CHANGELOG.md` | no change yet | Updated after implementation, not during planning |
   | `[new concept]/CLAUDE.md` | new file required | Feature introduces a new concept? |

   Ask the user to confirm the triage before proceeding. If they want to adjust which docs get touched, revise and re-confirm.

5. **Write PROJECT_PLAN.md entry** — Append or insert the new item into the appropriate section (Now / Next / Later). Use this format:

   ```markdown
   **[N]. [Feature Name]**
   - **What**: [One sentence description of what this builds]
   - **Why**: [The user-facing or technical reason it's needed]
   - **Who**: [Assignee or TBD]
   - **Status**: [Not started / In progress / Blocked]
   - **Depends on**: [Prerequisite features or decisions, if any]
   - **Tracking**: [Issue/ticket link, or "TBD"]
   ```

   Renumber existing items in the section if needed to maintain sequential numbering. Do not modify items in other sections.

6. **Apply remaining doc updates** — For each document marked `needs update` in the triage (except PROJECT_PLAN.md, already done):
   - If a concept CLAUDE.md needs new state/actions/invariants: add them in the correct tables. If the changes are substantial, suggest running `/concept-spec` instead to generate a fresh spec.
   - If SYNCHRONIZATIONS.md needs a new entry: suggest running `/sync-flow` to add it properly, rather than writing it manually here.
   - If ROADMAP.md needs an initiative update: add the feature under the current quarter's Key Initiatives or flag it as a new initiative if it doesn't fit any existing one.

7. **Confirm** — Output a short summary:
   - Files updated and what changed in each
   - Any files that need follow-up (e.g. "Run `/sync-flow` to define the cross-concept event flow", "Run `/concept-spec` to create the new concept")
   - If the feature introduces a new concept with no CLAUDE.md: "This feature needs a concept spec — run `/concept-spec` next."

---

## Rules

- Never add a feature to Now if PROJECT_PLAN.md already has 3+ active Now items — flag this and ask the user if something should move to Next first
- Never touch CHANGELOG.md during planning — it's updated after implementation, not before
- If the feature description implies cross-concept coordination (two or more concept names appear, or the flow crosses a module boundary), always mark SYNCHRONIZATIONS.md as `needs update` and direct the user to `/sync-flow`
- Do not invent tracking links — use "TBD" when none are provided
- Keep the PROJECT_PLAN.md entry concise; this is a planning artifact, not a spec. The concept CLAUDE.md is the spec.
- Strategic alignment in the entry ("Supports Q2 initiative: X") is optional but encouraged when the roadmap connection is clear

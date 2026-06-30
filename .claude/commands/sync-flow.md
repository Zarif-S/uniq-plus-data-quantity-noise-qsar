# Sync Flow

Add a new synchronization entry to `SYNCHRONIZATIONS.md` using the standard SYNC-NNN format from Meng & Jackson (2025).

## Steps

1. **Find the SYNCHRONIZATIONS.md file** — Look for it at the project root or in the nearest parent directory. If it doesn't exist yet, tell the user and offer to create it from the template before continuing.

2. **Read existing entries** — Scan the file to:
   - Determine the next SYNC-NNN number (e.g. if SYNC-003 is the last entry, the new one is SYNC-004)
   - Understand what concepts are already coordinated, to avoid duplication

3. **Gather information** — Ask the user for the following in a single message:
   - **Trigger**: which concept and action fires first (e.g. `MLWorkflow.evaluate(...)`)
   - **Condition**: what must be true for the downstream effect to fire, or "always"
   - **Effects**: which concept(s) and action(s) are called as a result, and how arguments are mapped from the trigger
   - **Rationale**: the user-facing behavior this produces and why it can't live inside either concept

   If the user has already described the flow in natural language (e.g. "when a model passes evaluation, it should be staged for deployment"), extract what you can from that description and only ask for what's missing.

4. **Validate before writing** — Flag any of the following and ask whether to proceed or revise:
   - Either concept referenced doesn't appear to exist (no matching CLAUDE.md found)
   - The trigger action isn't listed in the source concept's Actions table
   - The effect action isn't listed in the target concept's Actions table
   - The flow described is internal to a single concept (belongs in that concept's CLAUDE.md, not here)
   - A semantically identical or overlapping sync entry already exists

5. **Append the entry** — Insert the new SYNC entry at the end of the `## Synchronizations` section, before the `## Reference` section. Use the exact format below. Do not modify any existing entries.

6. **Update the footer** — If the `SYNCHRONIZATIONS.md` footer has a `**Concepts**:` line, add any newly referenced concepts that aren't already listed there.

7. **Confirm** — Tell the user:
   - The SYNC ID assigned (e.g. SYNC-004)
   - The file updated
   - Which concept CLAUDE.md files should cross-reference this entry (suggest adding a note like "See [SYNC-004](../SYNCHRONIZATIONS.md#sync-004)" under the relevant action in each concept's Implementation Notes)

---

## Entry Format

```markdown
### [SYNC-NNN] [Short descriptive name]

**Trigger**: `ConceptA.action(arg1, arg2)`

**Condition**: [State condition that must hold, or "always"]

**Effects**:
- `ConceptB.action(mapped_arg)`

**Rationale**: [Why this coordination is needed. What user-facing behavior does it produce? Why can't it live inside either concept?]

---
```

---

## Rules

- One entry per user-facing coordination need — do not bundle unrelated flows into a single SYNC
- Never edit or renumber existing SYNC entries; IDs are stable references used in code reviews and cross-links
- The trigger is always a single action on a single concept; fan-out goes in Effects, not in multiple triggers
- Arguments in Effects must be traceable to the trigger's state or arguments — do not invent values
- If a condition references a threshold or config value, name where that value lives (e.g. "in `rollout_config`, not in either concept")
- Rationale must explain why the two concepts cannot know about each other — this is the key design insight, not boilerplate

# Concept Spec

Generate a new concept `CLAUDE.md` for the agentic coding framework using the standard Concept Specification format.

## Steps

1. **Gather information** — Ask the user for the following, all at once in a single message:
   - Concept name (e.g. `auth`, `billing`, `notification`)
   - Module path where the file should live (e.g. `src/auth/` or `concepts/billing/`)
   - Purpose: one sentence describing the user-facing need this concept serves
   - State fields: each field's name, type, and what it holds
   - Actions: each action's name, signature, and what it does
   - Invariants: properties that must always hold (data guarantees, boundary conditions, ordering rules)
   - Common tasks: 1–3 recurring developer tasks with steps or commands
   - Any known issues or implementation decisions worth documenting upfront

   If the user has already provided some of this, skip asking for what you already have.

2. **Validate before generating** — Before writing the file, flag any design issues:
   - Actions that mutate state owned by another concept (isolation violation)
   - Invariants that contradict each other
   - Missing return types on actions
   - State fields that should live in `SYNCHRONIZATIONS.md` instead (cross-concept data)

   Surface issues as a short warning and ask whether to proceed or revise.

3. **Generate the file** — Write `CLAUDE.md` to the specified path using the exact template below. Fill in all placeholders; do not leave any `[...]` unfilled.

4. **Update root navigation** — Open the root `CLAUDE.md` and add a row to the Documentation Navigation table pointing to the new file:
   ```
   │ [Concept name]     → [path/to/concept/CLAUDE.md] │
   ```
   Only add this row if the root `CLAUDE.md` has a navigation table. Do not modify any other part of the root file.

5. **Confirm** — Tell the user:
   - The file path created
   - Whether the root navigation was updated
   - The next step: "If this concept coordinates with others, define the event flow in `SYNCHRONIZATIONS.md` using `/sync-flow`."

---

## Template

```markdown
# [Concept Name] - [Project Name]

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../SYNCHRONIZATIONS.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: [Single sentence — what user-facing need does this concept serve?]

### State

| Field | Type | Description |
|-------|------|-------------|
| `field_name` | `Type` | [What it holds, who owns it] |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `action_name` | `(args) → ReturnType` | [What it does] |

### Invariants

- [Property that must always hold]
- [Data quality or correctness guarantee]
- [Boundary condition]

---

## Architecture

```
[ASCII diagram showing the main flow through this concept's actions]
```

---

## Common Tasks

### [Task name]

[Steps or commands]

---

## Implementation Notes

### [Pattern/Decision Name]

**Issue**: [What problem does this solve?]

**Solution**: [Approach chosen and why]

**Location**: `[file:line]`

---

## Known Issues & Solutions

**[✅ RESOLVED | 🔄 IN PROGRESS | ⚠️ KNOWN LIMITATION]: [Title]**
- **Issue**: [Description]
- **Solution/Workaround**: [How it's handled]
- **Location**: `[file:line]`

---

**Last Updated**: [YYYY-MM-DD] | **Status**: [Active / Production] | **Maintainer**: [Name]
```

---

## Rules

- Never put cross-concept coordination logic inside the generated file — always redirect to `SYNCHRONIZATIONS.md`
- The Architecture section must be an ASCII diagram, not prose
- Invariants must be falsifiable statements, not vague goals ("status must be one of X, Y, Z" not "status should be valid")
- If the user provides no known issues or implementation notes, omit those sections entirely rather than leaving placeholder text
- Keep breadcrumb paths relative and correct for the actual file location

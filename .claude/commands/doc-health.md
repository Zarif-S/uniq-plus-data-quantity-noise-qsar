# Doc Health

Scan all documentation files in the project for structural issues — broken breadcrumbs, stale dates, missing required sections, and orphaned files — and produce a prioritized fix list.

## Steps

1. **Discover all docs** — Find every Markdown file in the project:
   - Run a glob for `**/*.md` from the project root
   - Exclude: `node_modules/`, `.venv/`, `dist/`, `build/`, vendor directories
   - Group by type: root docs (`CLAUDE.md`, `ROADMAP.md`, `PROJECT_PLAN.md`, `CHANGELOG.md`, `SYNCHRONIZATIONS.md`), concept CLAUDE.md files (any `CLAUDE.md` in a subdirectory), and other docs

2. **Run checks** — For each file, run all checks below. Collect every issue with its file path, line number (if applicable), severity, and a one-line description.

3. **Report** — Output a single prioritized report (Critical → Warning → Info), then ask: "Want me to fix any of these automatically?"

4. **Fix on request** — If the user says yes (to all or specific items), apply fixes. For issues that require judgment (e.g. rewriting a stale date, adding missing content), show the proposed change and confirm before writing.

---

## Checks

### Breadcrumb checks (all CLAUDE.md files)

**[CRITICAL] Broken relative link**
- Parse all `[text](path)` links in Breadcrumbs sections
- Resolve each path relative to the file's location
- Flag any that point to a file that doesn't exist

**[WARNING] Missing breadcrumb section**
- Every `CLAUDE.md` (root and concept) must have a `## Breadcrumbs` section
- Flag files where this section is absent

**[WARNING] Missing isolation rule**
- Every concept CLAUDE.md (any CLAUDE.md not at the project root) must contain the isolation rule blockquote:
  `> **Isolation rule**: This file describes only what this concept owns...`
- Flag concept files where this line is absent

**[INFO] Breadcrumb points to wrong file**
- Concept CLAUDE.md files should link upward to the root CLAUDE.md, ROADMAP.md, PROJECT_PLAN.md, and SYNCHRONIZATIONS.md
- Flag if any of these standard breadcrumbs are missing from a concept file

---

### Date checks (all docs)

**[WARNING] Stale Last Updated date**
- Find lines matching `**Last Updated**: YYYY-MM-DD`
- Flag any date older than 90 days from today
- For PROJECT_PLAN.md specifically: flag if older than 30 days (it's a living document)

**[WARNING] Missing Last Updated line**
- Flag any doc that has no `**Last Updated**:` line at all

---

### Required section checks

**[CRITICAL] Root CLAUDE.md missing navigation table**
- The root CLAUDE.md must contain a Documentation Navigation table (look for the `┌─` ASCII table pattern or a markdown table with a `TASK` column)
- Flag if absent

**[WARNING] Concept CLAUDE.md missing Concept Specification**
- Every concept CLAUDE.md must have a `## Concept Specification` section with `### State`, `### Actions`, and `### Invariants` subsections
- Flag which subsections are missing

**[WARNING] Concept CLAUDE.md missing Architecture section**
- Every concept CLAUDE.md must have an `## Architecture` section containing an ASCII diagram (look for ` ``` ` block with box-drawing characters or arrows)
- Flag if absent or if the section exists but contains only prose

**[INFO] CHANGELOG.md missing Unreleased section**
- Flag if `CHANGELOG.md` exists but has no `## [Unreleased]` section

**[INFO] SYNCHRONIZATIONS.md has no entries**
- Flag if `SYNCHRONIZATIONS.md` exists but the `## Synchronizations` section contains only the template placeholder (no real SYNC-NNN entries)

---

### Orphan checks

**[WARNING] Concept CLAUDE.md not listed in root navigation**
- For every concept CLAUDE.md found, check whether its path appears in the root CLAUDE.md navigation table
- Flag concept files that are missing from the navigation table

**[INFO] Doc file with no inbound links**
- For every non-root Markdown file, check whether any other doc links to it
- Flag files that are never referenced (potential orphans or stale docs)

---

## Report Format

```
## Doc Health Report — [date]

### Critical (must fix)
- [file:line] BROKEN LINK: `../CLAUDE.md` → file not found
- [file] MISSING SECTION: root CLAUDE.md has no navigation table

### Warnings (should fix)
- [file] STALE DATE: Last Updated 2024-08-01 (>90 days ago)
- [file] ORPHANED: not listed in root navigation table
- [file] MISSING: no isolation rule blockquote

### Info (nice to fix)
- [file] UNRELEASED section empty in CHANGELOG.md
- [file] Never referenced by any other doc

---
X critical · Y warnings · Z info
[N files scanned]
```

---

## Rules

- Never auto-fix Critical or Warning issues without confirmation — show proposed changes first
- Info-level issues may be batch-fixed without per-item confirmation if the user approves
- Do not modify file content to fix a broken link if the target file genuinely doesn't exist — flag it and let the user decide whether to create the file or update the link
- When fixing a stale `Last Updated` date, set it to today's date only — do not infer when the content was actually last changed
- If zero issues are found, say so clearly: "All docs passed health checks."

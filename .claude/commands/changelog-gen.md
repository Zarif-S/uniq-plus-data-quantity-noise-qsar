# Changelog Gen

Parse recent git commits and generate suggested `CHANGELOG.md` entries under `[Unreleased]`, ready for review and edit before merging.

## Steps

1. **Read current state** — In parallel:
   - Run `git log --oneline --no-merges` to get the full commit list
   - Read `CHANGELOG.md` to find the most recent released version and its date, and the current contents of `[Unreleased]`

2. **Determine the commit range** — Find the commit that corresponds to the most recent version tag in CHANGELOG.md:
   - Try `git log --oneline --no-merges [latest-version-tag]..HEAD` to get only commits since the last release
   - If no git tags exist, fall back to asking the user: "What date or commit should I use as the cutoff?" then use `git log --oneline --no-merges --since="[date]"`
   - If CHANGELOG.md has no released versions yet, use all commits

3. **Filter commits** — Exclude commits that don't belong in a changelog:
   - Merge commits (already excluded by `--no-merges`)
   - Commits matching patterns: `chore:`, `ci:`, `wip:`, `fixup!`, `squash!`, `bump version`, `update deps`, lint/format-only changes
   - Commits already represented in the current `[Unreleased]` section

4. **Classify each commit** — Map to Keep a Changelog categories:

   | Category | Commit signals |
   |----------|---------------|
   | `Added` | `feat:`, `add`, `new`, `introduce`, `implement`, `create` |
   | `Changed` | `refactor:`, `perf:`, `update`, `improve`, `change`, `migrate`, `rename` |
   | `Fixed` | `fix:`, `bug`, `correct`, `resolve`, `patch` |
   | `Removed` | `remove`, `delete`, `drop`, `deprecate` + removal language |
   | `Deprecated` | `deprecate`, `sunset`, `mark.*deprecated` |
   | `Security` | `security`, `vuln`, `CVE`, `auth`, `sanitize`, `inject` |

   If a commit is ambiguous, use the best-fit category and flag it with `[?]` so the user can review.

5. **Draft entries** — Write human-readable bullet points, not raw commit messages:
   - Expand abbreviations and jargon into plain descriptions
   - Strip ticket numbers, PR numbers, and author names from the bullet text (they belong in commit metadata, not the changelog)
   - Consolidate related commits into a single bullet when they clearly address the same change
   - Prefix breaking changes with `**BREAKING**:`
   - For ML/data science projects: if a commit references a model, dataset, or experiment, preserve the metric or version number (e.g. "F1: 0.82 → 0.87")

6. **Present a draft** — Show the proposed `[Unreleased]` block as a diff-style preview. Only include categories that have at least one entry — omit empty ones. Format:

   ```markdown
   ## [Unreleased]

   ### Added
   - ...

   ### Fixed
   - ...
   ```

   Below the draft, list any commits marked `[?]` with their raw message and the category assigned, so the user can correct them.

7. **Ask for confirmation** — "Does this look right? I can adjust categories, rewrite any bullets, merge entries, or drop ones that don't belong before updating the file."

8. **Write the file** — After confirmation, replace the existing `[Unreleased]` section in `CHANGELOG.md` with the approved draft. Do not touch any released version sections.

9. **Suggest a version bump** — Based on the classified changes, suggest what the next version number should be:
   - Any `**BREAKING**` entry → major bump
   - Any `Added` entries → minor bump
   - Only `Fixed`, `Changed`, `Security` → patch bump

   State the suggestion but do not modify the version number — that happens at release time, not during changelog drafting.

---

## Rules

- Never rewrite or remove existing released version sections (`## [1.0.0]`, etc.)
- Never auto-commit the changelog — always show a preview and get confirmation first
- If `CHANGELOG.md` doesn't exist, create it from the framework template before populating it
- Keep bullets concise: one change per bullet, one sentence max
- Do not invent context not present in the commit message or diff — if a commit is cryptic, write the bullet as close to the raw message as possible and mark it `[?]`
- If the commit range is empty (no new commits since last release), say so clearly rather than generating an empty section

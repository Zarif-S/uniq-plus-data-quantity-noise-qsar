# REVIEW-SCHEDULE.md Format

`REVIEW-SCHEDULE.md` tracks concepts due for spaced retrieval practice. It lives at the workspace root alongside `MISSION.md`. At the start of every session, this file is checked before any new teaching begins.

## Template

```md
# {Topic} Review Schedule

| Concept | LR | Learned | Last Reviewed | Next Review | Interval |
|---------|----|---------|-----------    |-------------|----------|
| SMILES notation | LR-0001 | 2026-06-01 | 2026-06-08 | 2026-06-15 | 7d |
| Morgan fingerprints | LR-0003 | 2026-06-03 | 2026-06-03 | 2026-06-10 | 7d |
| Train/test leakage | LR-0005 | 2026-06-05 | 2026-06-05 | 2026-06-08 | 3d |
```

## Columns

| Column | Description |
|--------|-------------|
| **Concept** | The specific concept being tracked — match the glossary term or learning record title |
| **LR** | The learning record that established this concept (e.g. `LR-0001`) |
| **Learned** | Date the concept was first confirmed understood |
| **Last Reviewed** | Date of the most recent retrieval practice attempt |
| **Next Review** | Date on or after which this concept should be tested again |
| **Interval** | Current spacing interval (3d, 7d, 14d, 28d, 56d, 90d) |

## Interval Schedule

Use a doubling schedule with a floor and cap:

- Starting interval: **7d** (after a concept is first learned)
- After a **poor** retrieval: reset to **3d**
- After a **good** retrieval: double the interval (7d → 14d → 28d → 56d → cap at **90d**)

A concept at 90d is considered stable. It stays in the schedule but is rarely surfaced.

## Rules

- **Add on glossary entry.** Every time a term is added to `GLOSSARY.md`, add a corresponding row here with `interval: 7d` and `next_review` set to 7 days from today.
- **Update after every review.** After retrieval practice, update `last_reviewed`, `next_review`, and `interval` immediately — do not defer.
- **Max 3 per session.** If more than 3 concepts are overdue, prioritise the oldest `next_review` date. The rest carry over.
- **Do not add concepts that were merely covered.** Only concepts confirmed understood (evidenced in a learning record) belong here.
- **Poor recall is useful data.** When a reset occurs, add a brief note to the relevant learning record: what was forgotten and what the user said when tested.

# Contributing

UNIQ+ is a 6-week academic research project with OPIG, supervisors: Professor Fergus Imrie (OPIG), Acer Blake (OPIG), Charlotte Dean MBE (OPIG).

This file exists to document the internal workflow so that future-me/contributors (or an AI agent) can make changes safely.

---

## Before Making Changes

1. **Read the context files**: `CLAUDE.md` → `PROJECT_PLAN.md` → relevant `src/` module
2. **Activate the environment**: `source .venv/bin/activate`
3. **Run the tests**: `uv run pytest tests/` — all should pass before and after your change
4. **Verify any changed notebook runs top-to-bottom**: Kernel → Restart & Run All

---

## Documentation Update Checklist

After completing any non-trivial change, ask: **"Which docs does this affect?"**

- [ ] **ROADMAP.md** — research direction or milestone changed?
- [ ] **PROJECT_PLAN.md** — sprint task completed or new blocker found?
- [ ] **CLAUDE.md** — setup, structure, or common tasks changed?
- [ ] **CHANGELOG.md** — significant feature, fix, or dataset change?
- [ ] **DECISIONS.md** — a non-obvious technical choice was made?

---

## Contact

This is a research project for academic purposes. For questions or feedback, open an issue in the repository or contact Zarif directly.

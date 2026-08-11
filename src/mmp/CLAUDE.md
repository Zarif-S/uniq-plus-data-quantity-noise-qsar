# MMP — UNIQ+

## Breadcrumbs
- **Project setup** → [Root CLAUDE.md](../../CLAUDE.md)
- **Strategic context** → [ROADMAP.md](../../ROADMAP.md)
- **Current sprint** → [PROJECT_PLAN.md](../../PROJECT_PLAN.md)
- **Cross-module flows** → [SYNCHRONIZATIONS.md](../../SYNCHRONIZATIONS.md)
- **src overview** → [../CLAUDE.md](../CLAUDE.md)

> **Isolation rule**: This file describes only what this concept owns. Any coordination with other concepts belongs in SYNCHRONIZATIONS.md — not here.

---

## Concept Specification

**Purpose**: Build a Matched Molecular Pair (MMP) rule database from ADME SMILES + endpoint labels via the `mmpdb` CLI, and query it for statistically significant transformation rules — recreating the MMP analysis described in Fang et al. (2023, the ADME paper this project recreates).

### State

| Field | Type | Description |
|-------|------|-------------|
| *(stateless wrapper functions)* | — | State lives on disk as `mmpdb`-produced files (`.smi`, `.fragments`, `.mmpdb` SQLite database), not in Python |

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `write_smi_file` | `(df, smiles_col, id_col, path) → None` | Whitespace-delimited SMILES file for `mmpdb fragment` |
| `write_properties_file` | `(df, id_col, property_cols, path) → None` | Tab-separated property file for `mmpdb index --properties`; NaN → `*` (mmpdb's required missing-value sentinel — writing `"nan"` instead would parse as a real float and silently corrupt statistics) |
| `run_fragment` | `(smi_path, fragments_path, num_jobs=4) → None` | Runs `mmpdb fragment` |
| `run_index` | `(fragments_path, properties_path, db_path) → None` | Runs `mmpdb index`, producing a `.mmpdb` SQLite database |
| `significant_rules` | `(db_path, property_name, max_radius=3, min_pairs=5, max_p_value=0.05) → DataFrame` | Representative rules per Fang et al.'s filter: ≥`min_pairs` matched pairs, paired-t-test p<`max_p_value`, most specific environment radius ≤ `max_radius` |

### Paper-matched defaults

`run_fragment`/`run_index` pin their mmpdb parameters explicitly (`MMPDB_CUT_SMARTS`, `MMPDB_ROTATABLE_SMARTS`, `MMPDB_NUM_CUTS=3`, `MMPDB_MAX_HEAVIES=100`, `MMPDB_MAX_ROTATABLE_BONDS=10`, `MMPDB_MAX_VARIABLE_HEAVIES=10` in `mmp.py`). These are mmpdb's own built-in defaults — Fang et al.'s fragmentation/indexing section describes running mmpdb with its defaults, not a custom rule set. Pinning them explicitly means a future mmpdb version can't silently change what we run.

`max_radius=3` in `significant_rules` is **not** an mmpdb indexing flag — mmpdb always computes environment statistics at radius 0–5 during indexing (`rule_environment_statistics` has one row per rule per radius). Fang et al.'s "max radius 3" is a query-time choice about which of those rows to treat as the representative one per rule; `significant_rules` reimplements that selection (most specific radius ≤ 3 that clears the pair-count/p-value bar) directly in SQL.

### Known deviations from the paper (unresolved, not silently worked around)

Root cause: this project pins `rdkit==2023.9.5` project-wide (every other notebook depends on it for reproducibility), and `mmpdb>=3.x` requires `rdkit>=2024.3` — confirmed directly, `uv add "mmpdb==3.1.4"` fails outright on that conflict. `uv add mmpdb` therefore resolves to the newest compatible version, 2.1.

- **mmpdb version**: the paper used mmpdb 2.2-dev1 (never published to PyPI — pre-release, git-only); this project has `mmpdb==2.1`. Fragmentation/indexing behavior across that version gap has not been verified identical.
- **"Minimum heavy atoms per constant fragment = 0"**: the paper's appendix states this as a fragmentation-phase parameter. mmpdb 2.1's `fragment` CLI has no corresponding flag. However, 0 is a null constraint — "no minimum" is the same as not filtering at all, which is exactly what mmpdb 2.1 already does by omitting the flag. Confirmed via mmpdb 3.1.4 (which does have `--min-heavies-per-const-frag`, checked via `uvx --from mmpdb==3.1.4 mmpdb fragment --help`) that setting it to 0 produces byte-identical downstream rule statistics to 2.1's unset behavior. So this is a documentation gap, not a results gap — not worth an mmpdb version upgrade (which would also mean running mmpdb outside this project's venv, since 3.x conflicts with the rdkit pin above) to close a parameter that's already a no-op.

### Invariants

- Inputs are never mutated — all functions read a DataFrame and write to disk paths
- `run_fragment`/`run_index` shell out via `subprocess.run(check=True)` — raise `CalledProcessError` on failure rather than silently producing an empty database
- `significant_rules` returns exactly one row per rule that survives the filter (deduplicated by rule id, keeping the most specific qualifying radius)

---

## Common Tasks

### Build an MMP database and query one endpoint

```python
from src.mmp import write_smi_file, write_properties_file, run_fragment, run_index, significant_rules

write_smi_file(df, smiles_col="SMILES", id_col="Internal ID", path="adme.smi")
write_properties_file(df, id_col="Internal ID", property_cols=["HLM", "MDR1", "SOL", "RLM"], path="adme_props.csv")
run_fragment("adme.smi", "adme.fragments")
run_index("adme.fragments", "adme_props.csv", "adme.mmpdb")

rules = significant_rules("adme.mmpdb", property_name="HLM")
```

---

**Last Updated**: 2026-08-06 | **Status**: Active | **Maintainer**: Zarif

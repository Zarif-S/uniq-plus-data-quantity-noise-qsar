# Review checklist — MMP analysis (`01.7_adme_mmp_analysis.ipynb` + `src/mmp/`)

A finite, prioritised list for reviewing the MMP recreation. Ordered by how much a mistake there
would change the conclusions. Tick each line once you've confirmed it. Anchors are
`file:function` or `notebook §section (cell_id)`.

**Fastest path**: read `src/mmp/CLAUDE.md` first (one-page contract for every function), then work
Tier 1 → Tier 2. Tier 3 is prose/skim. The 7 tests in `tests/test_mmp.py` (all passing) already
pin the mechanical behaviour of the `src/mmp` functions, so you're checking *intent vs. paper*,
not *does it run*.

---

## Tier 1 — Verify. A bug here changes the science.

### 1. Paper values transcribed from Figure 8 — HIGHEST RISK
These ~30 numbers were typed by eye from the Figure 8 image. Open the figure and confirm each row.
Anchor: **§7 (`bb30abf4`)**, the `PAPER_FIG8` list. Format: endpoint → (mean, std, nPairs).

- [ ] Transform **1 H→CH₃**: HLM (0.14, 0.29, **993**) · MDR1 (0.05, 0.33, **837**) · SOL (−0.12, 0.50, **372**)
- [ ] Transform **2 H→F**: HLM (0.05, 0.23, **1243**) · MDR1 (−0.06, 0.30, **1170**) · SOL (−0.15, 0.52, **560**)
- [ ] Transform **3 H→OH**: HLM (−0.23, 0.35, **66**) · MDR1 (0.89, 0.52, **23**) · SOL (0.11, 0.10, **9**)
- [ ] Transform **4 H→Cl**: HLM (0.17, 0.40, **287**) · MDR1 (−0.12, 0.35, **204**) · SOL (−0.34, 0.53, **89**)
- [ ] Transform **5 H→NH₂**: HLM (−0.24, 0.42, **62**) · MDR1 (0.28, 0.50, **31**) · SOL = blank (omitted)
- [ ] Transform **6 CH₃→C≡N**: HLM (−0.22, 0.41, **51**) · MDR1 (0.38, 0.37, **42**) · SOL (−0.32, 0.71, **25**)
- [ ] Directions are transcribed as the paper's H→X (adding the group), matching the figure's arrows.

> Transforms 1 and 2 carry the headline "agreement with the paper" — double-check those two hardest.

### 2. mmpdb parameters match the paper's appendix
Anchor: **`src/mmp/mmp.py`**, constants block (lines ~8–16). Compare each against the appendix text.

- [ ] `MMPDB_CUT_SMARTS` = `[#6+0;!$(*=,#[!#6])]!@!=!#[!#0;!#1;!$([CH2]);!$([CH3][CH2])]`
- [ ] `MMPDB_ROTATABLE_SMARTS` = `[!$([NH]!@C(=O))&!D1&!$(*#*)]-&!@[!$([NH]!@C(=O))&!D1&!$(*#*)]`
- [ ] `MMPDB_NUM_CUTS` = 3 · `MMPDB_MAX_HEAVIES` = 100 · `MMPDB_MAX_ROTATABLE_BONDS` = 10
- [ ] `MMPDB_MAX_VARIABLE_HEAVIES` = 10 (indexing phase)
- [ ] Known gap: the paper's "minimum heavy atoms per constant fragment = 0" has no CLI flag in
      our mmpdb **2.1** (paper used **2.2-dev1**). Confirm you're comfortable this is a no-op
      default and not a silent divergence. (Version mismatch is itself worth noting in writeup.)

### 3. Significance filter logic
Anchor: **`src/mmp/mmp.py`**, `significant_rules()`. Drives the §5 counts.

- [ ] SQL filters `re.radius <= max_radius (3)` AND `res.count >= min_pairs (5)` AND `res.p_value < max_p_value (0.05)` — matches paper's stated criteria.
- [ ] Dedup keeps **one row per rule** at the **most specific** (highest) qualifying radius
      (`sort_values([rule_id, radius], ascending=[True, False])` then `drop_duplicates(keep='first')`).
- [ ] You accept this "most-specific-environment" choice for §5 (vs. §7's radius-0 aggregate).
      The two are documented as answering different questions — confirm that's acceptable, not a bug.

---

## Tier 2 — Check the plumbing. Wrong numbers, but obvious once spotted.

### 4. Data source & mmpdb input files
Anchor: **§2 (`c900276b`, `3b932333`)**.

- [ ] Loads `data/processed/section4_df_sdf.pkl` — the standardized, ChEMBL-augmented set from
      `01.5` §2.4 (the one you already trust), **not** the raw CSV.
- [ ] `write_smi_file` uses `smiles_col='can_smi'` (the standardized canonical SMILES), `id_col='compound_id'`.
- [ ] `write_properties_file` writes NaN as `*` (mmpdb's required missing sentinel), not `"nan"`.
- [ ] The 6 endpoint columns are renamed to short names before writing (mmpdb needs no-whitespace names).

### 5. Ring-transform SMILES encodings (illustrative, lower stakes)
Anchor: **§7.2 (`8a1b016f`)**, `REPRESENTATIVE_TRANSFORMS`. Group-1 encodings are unambiguous;
the ring ones were hand-written and could be subtly wrong (a wrong SMILES → wrong "structural pairs").

- [ ] T8 gem-diMe→cyclopropane: `[*:1]C(C)C` → `[*:1]C1CC1`
- [ ] T9 iPr→cyclobutane: `[*:1]C(C)C` → `[*:1]C1CCC1`
- [ ] T17 piperidine→morpholine: `[*:1]N1CCCCC1` → `[*:1]N1CCOCC1`
- [ ] (These feed only the §7.2 illustration, not any paper-comparison claim.)

### 6. Direction-flip logic in the Figure 8 comparison
Anchor: **§7 (`bb30abf4`)**, `lookup_transform()`.

- [ ] Reads **radius 0** stats (matches paper's large nPairs).
- [ ] Flips the sign of `mean_change` when mmpdb stored the transform in the reverse orientation
      (`if stored_from != paper_from: mean_change = -mean_change`) — so every number is in the paper's H→X convention.

---

## Tier 3 — Skim for story, not correctness.

- [ ] **§1** setup / **§3 (`41d468c6`)** fragment+index — mechanical; trust the tests.
- [ ] **§4 (`ede7e98e`)** scale vs paper; **§4.1/§4.2** funnel — read the narrative; numbers are computed live.
- [ ] **§5 (`84c7ce97`, `753d1cda`)** representative-rules output — sanity-check the printed rules look chemically sane.
- [ ] **§6 (`7fcf7785`)** summary bar chart.
- [ ] **§7.1 (`fe7ec640`)** exhaustive ≥5-pair list — confirms only small functional-group swaps survive.
- [ ] **§8 (`36ed8ebe`)** discussion — read for whether the story matches your understanding:
      data-quantity effect, structural-pairs-present-but-label-starved, PPB is beyond-paper.

---

## Cross-cutting claims to keep in mind while reading

- [ ] **PPB is an extension, not a recreation** — the paper's Figure 8 is HLM/MDR1/solubility only.
      Every place PPB_H/PPB_R appears should be framed as beyond-paper (§5 markdown, §8).
- [ ] **The bottleneck is paired assay labels, not structures** — the §7.2 table is the evidence;
      confirm the "structural pairs" column is healthy while "assay pairs" collapses.
- [ ] **§5 vs §7 report the same rule at different radii** — this is intentional and documented in
      the §7 markdown; confirm the explanation reads clearly.

---

*Generated as a review aid. Delete once the review is complete, or keep as a record of what was verified.*

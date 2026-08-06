"""Matched Molecular Pair (MMP) database construction and rule querying, via the mmpdb CLI."""

import sqlite3
import subprocess

import pandas as pd

# mmpdb's own built-in defaults, pinned explicitly so a future mmpdb version can't silently
# change what we run. These are also the exact values Fang et al. (2023) describe using -- the
# paper's fragmentation/indexing section is describing mmpdb's defaults, not a custom rule set.
MMPDB_CUT_SMARTS = "[#6+0;!$(*=,#[!#6])]!@!=!#[!#0;!#1;!$([CH2]);!$([CH3][CH2])]"
MMPDB_ROTATABLE_SMARTS = "[!$([NH]!@C(=O))&!D1&!$(*#*)]-&!@[!$([NH]!@C(=O))&!D1&!$(*#*)]"
MMPDB_NUM_CUTS = 3
MMPDB_MAX_HEAVIES = 100
MMPDB_MAX_ROTATABLE_BONDS = 10
MMPDB_MAX_VARIABLE_HEAVIES = 10


def write_smi_file(df, smiles_col, id_col, path):
    """Write a whitespace-delimited SMILES file (SMILES, id per line) for `mmpdb fragment`."""
    with open(path, "w") as f:
        for smiles, compound_id in zip(df[smiles_col], df[id_col]):
            f.write(f"{smiles} {compound_id}\n")


def write_properties_file(df, id_col, property_cols, path):
    """Write a tab-separated property file for `mmpdb index --properties`; NaN values become '*'."""
    header = ["ID"] + list(property_cols)
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for _, row in df.iterrows():
            values = [str(row[col]) if pd.notna(row[col]) else "*" for col in property_cols]
            f.write("\t".join([str(row[id_col])] + values) + "\n")


def run_fragment(smi_path, fragments_path, num_jobs=4):
    """Run `mmpdb fragment` on `smi_path`, with parameters pinned to mmpdb's defaults (== Fang et al. 2023)."""
    subprocess.run(
        [
            "mmpdb", "fragment", str(smi_path),
            "-o", str(fragments_path),
            "--cut-smarts", MMPDB_CUT_SMARTS,
            "--num-cuts", str(MMPDB_NUM_CUTS),
            "--max-heavies", str(MMPDB_MAX_HEAVIES),
            "--max-rotatable-bonds", str(MMPDB_MAX_ROTATABLE_BONDS),
            "--rotatable-smarts", MMPDB_ROTATABLE_SMARTS,
            "--num-jobs", str(num_jobs),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def run_index(fragments_path, properties_path, db_path):
    """Run `mmpdb index` on `fragments_path`, with max-variable-heavies pinned to mmpdb's default (== Fang et al. 2023)."""
    subprocess.run(
        [
            "mmpdb", "index", str(fragments_path),
            "--properties", str(properties_path),
            "--max-variable-heavies", str(MMPDB_MAX_VARIABLE_HEAVIES),
            "-o", str(db_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def significant_rules(db_path, property_name, max_radius=3, min_pairs=5, max_p_value=0.05):
    """Representative MMP rules for `property_name`, following Fang et al.'s significance filter.

    mmpdb stores one row per (rule, environment radius) in `rule_environment_statistics`, with
    radius ranging 0-5 by default. For each rule, keep only the most specific surviving
    environment: the largest radius (<= max_radius) with at least `min_pairs` matched pairs and a
    paired-t-test p-value below `max_p_value` (mirrors mmpdb's own most-specific-environment
    selection used by `mmpdb predict`/`transform`). One row per surviving rule, sorted by mean
    property change ascending (most negative first).
    """
    con = sqlite3.connect(db_path)
    query = """
        select r.id as rule_id, rs1.smiles as from_smiles, rs2.smiles as to_smiles,
               re.radius as radius, res.count as n_pairs, res.avg as mean_change,
               res.std as std_change, res.p_value as p_value
        from rule_environment_statistics res
        join rule_environment re on res.rule_environment_id = re.id
        join rule r on re.rule_id = r.id
        join rule_smiles rs1 on r.from_smiles_id = rs1.id
        join rule_smiles rs2 on r.to_smiles_id = rs2.id
        join property_name pn on res.property_name_id = pn.id
        where pn.name = ? and re.radius <= ? and res.count >= ? and res.p_value < ?
    """
    df = pd.read_sql_query(query, con, params=(property_name, max_radius, min_pairs, max_p_value))
    con.close()
    if df.empty:
        return df
    df = df.sort_values(["rule_id", "radius"], ascending=[True, False])
    df = df.drop_duplicates(subset="rule_id", keep="first")
    return df.sort_values("mean_change").reset_index(drop=True)
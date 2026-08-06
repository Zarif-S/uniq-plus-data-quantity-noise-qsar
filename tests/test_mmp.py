"""Sanity tests for src/mmp."""

import sqlite3

import pandas as pd
import pytest

from src.mmp import run_fragment, run_index, significant_rules, write_properties_file, write_smi_file


@pytest.fixture
def toy_df():
    return pd.DataFrame(
        {
            "id": ["mol1", "mol2", "mol3", "mol4", "mol5", "mol6"],
            "smiles": [
                "c1ccccc1C",
                "c1ccccc1CC",
                "c1ccccc1CCC",
                "Clc1ccccc1C",
                "Fc1ccccc1C",
                "c1ccccc1C",
            ],
            "val": [1.0, 1.5, 2.0, 3.0, 2.5, 1.1],
        }
    )


@pytest.fixture
def toy_db(toy_df, tmp_path):
    smi_path = tmp_path / "toy.smi"
    props_path = tmp_path / "toy_props.csv"
    fragments_path = tmp_path / "toy.fragments"
    db_path = tmp_path / "toy.mmpdb"
    write_smi_file(toy_df, "smiles", "id", smi_path)
    write_properties_file(toy_df, "id", ["val"], props_path)
    run_fragment(smi_path, fragments_path)
    run_index(fragments_path, props_path, db_path)
    return db_path


class TestWriteSmiFile:
    def test_one_line_per_compound(self, toy_df, tmp_path):
        path = tmp_path / "out.smi"
        write_smi_file(toy_df, "smiles", "id", path)
        lines = path.read_text().splitlines()
        assert len(lines) == len(toy_df)
        assert lines[0] == "c1ccccc1C mol1"


class TestWritePropertiesFile:
    def test_header_and_missing_value_sentinel(self, tmp_path):
        df = pd.DataFrame({"id": ["a", "b"], "val": [1.0, float("nan")]})
        path = tmp_path / "props.csv"
        write_properties_file(df, "id", ["val"], path)
        lines = path.read_text().splitlines()
        assert lines[0] == "ID\tval"
        assert lines[1] == "a\t1.0"
        assert lines[2] == "b\t*"


class TestRunFragmentIndex:
    def test_produces_queryable_mmpdb(self, toy_db):
        con = sqlite3.connect(toy_db)
        cur = con.cursor()
        cur.execute("select count(*) from rule")
        assert cur.fetchone()[0] > 0
        con.close()


class TestSignificantRules:
    def test_finds_known_halogen_to_hydrogen_effect(self, toy_db):
        df = significant_rules(toy_db, "val", max_radius=3, min_pairs=1, max_p_value=1.0)
        cl_to_h = df[(df["from_smiles"] == "[*:1]Cl") & (df["to_smiles"] == "[*:1][H]")]
        assert len(cl_to_h) == 1
        assert cl_to_h.iloc[0]["mean_change"] < 0

    def test_one_row_per_rule(self, toy_db):
        df = significant_rules(toy_db, "val", max_radius=3, min_pairs=1, max_p_value=1.0)
        assert df["rule_id"].is_unique

    def test_sorted_ascending_by_mean_change(self, toy_db):
        df = significant_rules(toy_db, "val", max_radius=3, min_pairs=1, max_p_value=1.0)
        assert (df["mean_change"].diff().dropna() >= 0).all()

    def test_strict_min_pairs_can_empty_result(self, toy_db):
        df = significant_rules(toy_db, "val", max_radius=3, min_pairs=1000, max_p_value=1.0)
        assert df.empty

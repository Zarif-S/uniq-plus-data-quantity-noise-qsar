"""Sanity tests for src/eda.py."""

import numpy as np
import pandas as pd
import pytest
from src.eda import missing_value_report, smiles_validity_report


VALID_SMILES = "CCO"
INVALID_SMILES = "not_a_smiles"


def test_smiles_validity_report_counts():
    df = pd.DataFrame({
        "SMILES": [VALID_SMILES, VALID_SMILES, INVALID_SMILES, None]
    })
    report = smiles_validity_report(df)
    assert report["valid_count"] == 2
    assert report["invalid_count"] == 2
    assert len(report["invalid_indices"]) == 2


def test_missing_value_report_percentages():
    df = pd.DataFrame({
        "ep1": [1.0, np.nan, 3.0, 4.0],
        "ep2": [np.nan, np.nan, 3.0, 4.0],
    })
    report = missing_value_report(df, ["ep1", "ep2"])
    assert report.loc["ep1", "n_missing"] == 1
    assert report.loc["ep2", "n_missing"] == 2
    assert report.loc["ep1", "pct_missing"] == 25.0
    assert report.loc["ep2", "pct_missing"] == 50.0

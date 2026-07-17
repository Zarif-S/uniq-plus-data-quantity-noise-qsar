"""Sanity tests for src/cleaning."""

import numpy as np
import pandas as pd
import pytest
from src.cleaning import exclude_stereoisomer_pairs, filter_endpoint, flag_iqr_outliers


# ── exclude_stereoisomer_pairs ────────────────────────────────────────────────

@pytest.fixture
def stereo_df():
    # Two enantiomers of bromochlorofluoromethane; ep1 differs by 1.0 log unit (>log10(3)≈0.477)
    return pd.DataFrame({
        "SMILES": ["[C@@H](F)(Cl)Br", "[C@H](F)(Cl)Br", "CCO"],
        "ep1": [1.0, 2.0, 1.5],   # pair differs by 1.0 > 0.477 → excluded
        "ep2": [0.5, 0.6, 0.5],   # pair differs by 0.1 < 0.477 → fine alone
    })


def test_exclude_stereoisomer_pairs_removes_outlier_pair(stereo_df):
    result, excluded = exclude_stereoisomer_pairs(stereo_df, "SMILES", ["ep1", "ep2"])
    assert len(result) == 1
    assert result["SMILES"].iloc[0] == "CCO"


def test_exclude_stereoisomer_pairs_excluded_indices(stereo_df):
    _, excluded = exclude_stereoisomer_pairs(stereo_df, "SMILES", ["ep1", "ep2"])
    assert set(excluded) == {0, 1}


def test_exclude_stereoisomer_pairs_no_mutation(stereo_df):
    original_len = len(stereo_df)
    exclude_stereoisomer_pairs(stereo_df, "SMILES", ["ep1", "ep2"])
    assert len(stereo_df) == original_len


def test_exclude_stereoisomer_pairs_keeps_close_pair():
    # ep1 differs by 0.2 < log10(3) → pair should survive
    df = pd.DataFrame({
        "SMILES": ["[C@@H](F)(Cl)Br", "[C@H](F)(Cl)Br"],
        "ep1": [1.0, 1.2],
    })
    result, excluded = exclude_stereoisomer_pairs(df, "SMILES", ["ep1"])
    assert len(excluded) == 0
    assert len(result) == 2


def test_exclude_stereoisomer_pairs_ignores_nan_endpoints():
    # ep1 is NaN for one compound — cannot compare, pair should survive
    df = pd.DataFrame({
        "SMILES": ["[C@@H](F)(Cl)Br", "[C@H](F)(Cl)Br"],
        "ep1": [1.0, np.nan],
    })
    result, excluded = exclude_stereoisomer_pairs(df, "SMILES", ["ep1"])
    assert len(excluded) == 0


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "SMILES": ["CCO", "CCC", "CCCO", "CCCCO"],
            "ep1": [1.0, np.nan, 3.0, 4.0],
            "ep2": [0.5, 1.5, 2.5, 3.5],
        }
    )


def test_filter_endpoint_drops_nan(sample_df):
    result = filter_endpoint(sample_df, "ep1")
    assert result["ep1"].isna().sum() == 0


def test_filter_endpoint_preserves_other_cols(sample_df):
    result = filter_endpoint(sample_df, "ep1")
    assert "ep2" in result.columns
    assert "SMILES" in result.columns
    assert len(result) == 3


def test_filter_endpoint_no_mutation(sample_df):
    original_len = len(sample_df)
    filter_endpoint(sample_df, "ep1")
    assert len(sample_df) == original_len


def test_flag_iqr_outliers_returns_bool_series(sample_df):
    mask = flag_iqr_outliers(sample_df, "ep2")
    assert mask.dtype == bool
    assert list(mask.index) == list(sample_df.index)


def test_flag_iqr_outliers_no_mutation(sample_df):
    original = sample_df["ep2"].copy()
    flag_iqr_outliers(sample_df, "ep2")
    pd.testing.assert_series_equal(sample_df["ep2"], original)


def test_flag_iqr_outliers_raises_on_nan(sample_df):
    with pytest.raises(ValueError, match="contains NaN"):
        flag_iqr_outliers(sample_df, "ep1")


def test_flag_iqr_outliers_detects_extreme_values():
    # pandas linear interpolation: Q1=2.25, Q3=4.75, IQR=2.5 → lower=-1.5, upper=8.5
    # → 100.0 flagged, 1.0 not flagged
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]})
    mask = flag_iqr_outliers(df, "val")
    assert mask.iloc[-1] == True   # 100.0 is an outlier
    assert mask.iloc[0] == False   # 1.0 is within bounds

"""Sanity tests for src/cleaning."""

import numpy as np
import pandas as pd
import pytest
from src.cleaning import filter_endpoint, flag_iqr_outliers


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

"""Sanity tests for src/splitting."""

import pandas as pd
import pytest
from src.splitting import get_split, list_split_cols, SPLIT_COLS


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "SMILES": ["CCO", "CCC", "CCCO", "CCCCO", "CCCCCO"],
            "pic50": [7.0, 8.0, 6.5, 7.5, 9.0],
            "random_split": ["train", "train", "test", "val", "train"],
            "other_split": ["train", "test", "train", "test", "train"],
        }
    )


def test_get_split_returns_correct_rows(sample_df):
    train_df, test_df = get_split(sample_df, "random_split")
    assert (train_df["random_split"] == "train").all()
    assert (test_df["random_split"] == "test").all()


def test_get_split_excludes_val(sample_df):
    train_df, test_df = get_split(sample_df, "random_split")
    assert "val" not in train_df["random_split"].values
    assert "val" not in test_df["random_split"].values


def test_get_split_disjoint(sample_df):
    train_df, test_df = get_split(sample_df, "random_split")
    assert len(set(train_df.index) & set(test_df.index)) == 0


def test_get_split_no_mutation(sample_df):
    original = sample_df["random_split"].copy()
    get_split(sample_df, "random_split")
    pd.testing.assert_series_equal(sample_df["random_split"], original)


def test_get_split_raises_on_unknown_col(sample_df):
    with pytest.raises(ValueError, match="not found in DataFrame columns"):
        get_split(sample_df, "nonexistent_split")


def test_list_split_cols_returns_only_present(sample_df):
    present = list_split_cols(sample_df)
    # sample_df has "random_split" and "other_split"; only random_split is in SPLIT_COLS
    assert "random_split" in present
    assert "other_split" not in present
    # all returned cols must be in SPLIT_COLS
    assert all(col in SPLIT_COLS for col in present)

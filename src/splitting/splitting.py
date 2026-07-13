"""Pre-defined train/test split extraction for PDE10A QSAR experiments."""

SPLIT_COLS = [
    "aminohetaryl_c1_amide_split",
    "aryl_c1_amide_c2_hetaryl_split",
    "temporal_2012_split",
    "c1_hetaryl_alkyl_c2_hetaryl_split",
    "temporal_2013_split",
    "temporal_2011_split",
    "random_split",
]


def get_split(df, split_col):
    """Return (train_df, test_df) by filtering on split_col; val rows are discarded.

    Raises ValueError if split_col is not in df.columns or if either partition is empty.
    Source DataFrame is never mutated.
    """
    if split_col not in df.columns:
        raise ValueError(f"get_split: '{split_col}' not found in DataFrame columns.")
    train_df = df[df[split_col] == "train"].copy()
    test_df = df[df[split_col] == "test"].copy()
    if train_df.empty:
        raise ValueError(f"get_split: no 'train' rows found in column '{split_col}'.")
    if test_df.empty:
        raise ValueError(f"get_split: no 'test' rows found in column '{split_col}'.")
    return train_df, test_df


def list_split_cols(df):
    """Return the subset of SPLIT_COLS present in df.columns."""
    return [col for col in SPLIT_COLS if col in df.columns]

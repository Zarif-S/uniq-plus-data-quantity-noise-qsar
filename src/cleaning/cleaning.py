"""Per-endpoint missing value filtering and IQR outlier detection for UNIQ+."""


def filter_endpoint(df, endpoint_col):
    """Return DataFrame with rows where endpoint_col is NaN removed."""
    return df[df[endpoint_col].notna()].copy()


def flag_iqr_outliers(df, endpoint_col, k=1.5):
    """Return boolean Series (True = outlier) using the k*IQR rule.

    Rows outside [Q1 - k*IQR, Q3 + k*IQR] are flagged. Source DataFrame is not modified.
    Raises ValueError if endpoint_col contains NaN — call filter_endpoint first.
    """
    col = df[endpoint_col]
    if col.isna().any():
        raise ValueError(
            f"flag_iqr_outliers: '{endpoint_col}' contains NaN. "
            "Call filter_endpoint first."
        )
    q1, q3 = col.quantile(0.25), col.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (col < lower) | (col > upper)

"""Per-endpoint missing value filtering and IQR outlier detection for UNIQ+."""

import numpy as np
import pandas as pd
from rdkit import Chem


def exclude_stereoisomer_pairs(df, smiles_col, endpoint_cols, fold_threshold=3):
    """Return (filtered_df, excluded_indices) removing stereoisomers with >fold_threshold-fold
    difference in any log-scale endpoint.

    Identifies compounds sharing the same flat (stereo-stripped) canonical SMILES.
    For each such pair, if any endpoint where both values are non-NaN differs by more than
    log10(fold_threshold), both compounds are excluded. Source DataFrame is not modified.
    """
    log_thresh = np.log10(fold_threshold)

    def _to_flat(smi):
        mol = Chem.MolFromSmiles(str(smi))
        return Chem.MolToSmiles(mol, isomericSmiles=False) if mol is not None else None

    flat_smiles = df[smiles_col].apply(_to_flat)

    exclude = set()
    for _, idxs in flat_smiles.groupby(flat_smiles).groups.items():
        idxs = list(idxs)
        if len(idxs) < 2:
            continue
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                for col in endpoint_cols:
                    a = df.loc[idxs[i], col]
                    b = df.loc[idxs[j], col]
                    if pd.notna(a) and pd.notna(b) and abs(a - b) > log_thresh:
                        exclude.update([idxs[i], idxs[j]])
                        break  # one endpoint exceeding threshold is sufficient

    excluded = sorted(exclude)
    return df.drop(index=excluded).reset_index(drop=True), excluded


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

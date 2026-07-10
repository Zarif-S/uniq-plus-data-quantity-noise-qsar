"""EDA utilities for UNIQ+ ADME dataset analysis."""

import pandas as pd
from rdkit import Chem


def smiles_validity_report(df, smiles_col="SMILES"):
    """Return dict: valid_count, invalid_count, invalid_indices."""
    results = {"valid_count": 0, "invalid_count": 0, "invalid_indices": []}
    for idx, smi in df[smiles_col].items():
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is not None:
            results["valid_count"] += 1
        else:
            results["invalid_count"] += 1
            results["invalid_indices"].append(idx)
    return results


def missing_value_report(df, endpoint_cols):
    """Return DataFrame of N missing and % missing per endpoint column."""
    n_missing = df[endpoint_cols].isna().sum()
    pct_missing = (n_missing / len(df) * 100).round(2)
    report = pd.DataFrame({"n_missing": n_missing, "pct_missing": pct_missing})
    return report

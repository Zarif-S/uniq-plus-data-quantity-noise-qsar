"""EDA utilities for UNIQ+ ADME dataset analysis."""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator, DataStructs
from sklearn.metrics import r2_score
from useful_rdkit_utils import max_possible_correlation


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

FOLD_LEVELS = [2, 3, 5, 10]


def _r2_score_method(y_true, y_pred):
    """Adapt sklearn's r2_score to the (score, ...) tuple contract max_possible_correlation expects."""
    return (r2_score(y_true, y_pred), None)


def max_corr_report(df, endpoint_cols, fold_levels=None, cycles=1000, metric="pearson_r2"):
    """Upper bound on achievable R² per endpoint at multiple assay noise levels.

    Follows Pat Walters' approach (Brown, Muchmore & Hajduk noise model): for each
    fold-change level, adds Gaussian noise of std=log10(fold) to the endpoint values
    and compares the noisy realization against the original over `cycles` iterations.

    metric="pearson_r2" (default): mean Pearson r across cycles, then squared — matches
    the original Brown/Muchmore/Hajduk reproducibility framing (symmetric, calibration-blind;
    two noisy views of the same underlying quantity, neither privileged as "truth").
    metric="r2": mean sklearn r2_score(original, noisy) across cycles, used as-is (already
    an R² value, not squared) — asymmetric and calibration-sensitive, for overlaying against
    model curves that are themselves scored with r2_score (e.g. the systematic_bias noise
    panel in 04_adme_noise.ipynb, where calibration damage is the point being measured).

    fold_levels: list of fold-change magnitudes to evaluate (default: [2, 3, 5, 10]).
    Returns a DataFrame with n (valid rows) + one R² column per fold level.
    """
    import numpy as np

    if metric not in ("pearson_r2", "r2"):
        raise ValueError(f"Unknown metric: {metric!r} (expected 'pearson_r2' or 'r2')")

    if fold_levels is None:
        fold_levels = FOLD_LEVELS

    rows = []
    for col in endpoint_cols:
        vals = df[col].dropna().values.astype(float)
        row = {"endpoint": col, "n": len(vals)}
        if len(vals) < 2:
            for fold in fold_levels:
                row[f"{fold}-Fold"] = float("nan")
        else:
            vals_list = vals.tolist()
            for fold in fold_levels:
                if metric == "pearson_r2":
                    r = max_possible_correlation(vals_list, error=np.log10(fold), cycles=cycles)
                    row[f"{fold}-Fold"] = r ** 2
                else:
                    row[f"{fold}-Fold"] = max_possible_correlation(
                        vals_list, error=np.log10(fold), cycles=cycles, method=_r2_score_method,
                    )
        rows.append(row)
    return pd.DataFrame(rows).set_index("endpoint")


def pairwise_tanimoto(smiles_list, radius=2, n_bits=2048):
    """Compute all pairwise Tanimoto similarities for a list of SMILES.

    Uses RDKit's BulkTanimotoSimilarity for speed: for each molecule i,
    computes Tanimoto against all molecules j > i (upper triangle only),
    giving N*(N-1)/2 pairs total. Internally works with ExplicitBitVect
    objects so the comparison runs in optimized C++.

    Returns a 1-D numpy array of similarity values (upper triangle, no diagonal).
    """
    # Generate Morgan fingerprints as ExplicitBitVect objects (not numpy)
    # BulkTanimotoSimilarity requires these native RDKit bit vectors
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        fps.append(gen.GetFingerprint(mol))

    # Upper triangle: compare each molecule to all subsequent ones
    # BulkTanimotoSimilarity(fp_i, [fp_j, ...]) returns a list of floats
    sims = []
    n = len(fps)
    for i in range(n - 1):
        bulk = DataStructs.BulkTanimotoSimilarity(fps[i], fps[i + 1:])
        sims.extend(bulk)

    return np.array(sims)

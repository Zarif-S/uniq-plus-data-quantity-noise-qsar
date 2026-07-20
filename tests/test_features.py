"""Sanity tests for src/features.py."""

import numpy as np
import pytest
from src.features import morgan_fingerprints, rdkit_descriptors


ETHANOL = "CCO"
ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"


def test_morgan_fp_shape():
    fps = morgan_fingerprints([ETHANOL])
    assert fps.shape == (1, 2048)


def test_morgan_fp_shape_multiple():
    fps = morgan_fingerprints([ETHANOL, ASPIRIN])
    assert fps.shape == (2, 2048)


def test_morgan_fp_invalid_smiles_raises_value_error():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        morgan_fingerprints(["not_valid"])


def test_rdkit_descriptors_invalid_smiles_raises_value_error():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        rdkit_descriptors(["not_valid"])


def test_rdkit_descriptors_columns():
    df = rdkit_descriptors([ETHANOL])
    expected = {"MW", "LogP", "TPSA", "HBD", "HBA", "RotBonds"}
    assert expected.issubset(set(df.columns))


def test_rdkit_descriptors_values_not_nan():
    df = rdkit_descriptors([ASPIRIN])
    assert not df.iloc[0].isna().any()


# --- rdkit_2d_features tests ---

from src.features import rdkit_2d_features


def test_rdkit_2d_features_shape():
    X = rdkit_2d_features([ETHANOL, ASPIRIN])
    assert X.shape == (2, 200)


def test_rdkit_2d_features_invalid_smiles_raises():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        rdkit_2d_features(["not_valid"])


def test_rdkit_2d_features_no_nans():
    X = rdkit_2d_features([ASPIRIN, ETHANOL])
    assert not np.any(np.isnan(X))

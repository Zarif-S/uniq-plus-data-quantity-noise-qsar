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


def test_morgan_fp_invalid_smiles_returns_zeros():
    fps = morgan_fingerprints(["not_valid"])
    assert fps.shape == (1, 2048)
    assert fps[0].sum() == 0


def test_rdkit_descriptors_columns():
    df = rdkit_descriptors([ETHANOL])
    expected = {"MW", "LogP", "TPSA", "HBD", "HBA", "RotBonds"}
    assert expected.issubset(set(df.columns))


def test_rdkit_descriptors_values_not_nan():
    df = rdkit_descriptors([ASPIRIN])
    assert not df.iloc[0].isna().any()

"""Sanity tests for src/features.py."""

import numpy as np
import pytest
from rdkit import Chem
from rdkit.Chem import AllChem
from src.features import morgan_fingerprints, rdkit_descriptors, rdmoldes


ETHANOL = "CCO"
ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"


def _mol_with_conformer(smiles):
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    return mol


def test_morgan_fp_shape():
    fps = morgan_fingerprints([ETHANOL])
    assert fps.shape == (1, 1024)


def test_morgan_fp_shape_multiple():
    fps = morgan_fingerprints([ETHANOL, ASPIRIN])
    assert fps.shape == (2, 1024)


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


# --- rdmoldes tests ---


def test_rdmoldes_shape():
    mols = [_mol_with_conformer(ETHANOL), _mol_with_conformer(ASPIRIN)]
    X = rdmoldes(mols)
    assert X.shape == (2, 316)


def test_rdmoldes_none_mol_raises():
    with pytest.raises(ValueError):
        rdmoldes([None])


def test_rdmoldes_no_nans():
    mols = [_mol_with_conformer(ASPIRIN), _mol_with_conformer(ETHANOL)]
    X = rdmoldes(mols)
    assert not np.any(np.isnan(X))


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

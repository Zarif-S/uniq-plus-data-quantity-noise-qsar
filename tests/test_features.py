"""Sanity tests for src/features.py."""

import numpy as np
import pytest
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from src.features import morgan_fingerprints, rdkit_descriptors, rdmoldes, fcfp4_bit_vectors


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


def test_morgan_fp_use_features_false_gives_ecfp4_and_differs():
    # use_features=False -> ECFP4 numpy matrix; must differ from the FCFP4 default for aspirin
    fcfp4 = morgan_fingerprints([ASPIRIN], use_features=True)
    ecfp4 = morgan_fingerprints([ASPIRIN], use_features=False)
    assert ecfp4.shape == (1, 1024)
    assert not np.array_equal(fcfp4, ecfp4)


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


# --- fcfp4_bit_vectors tests ---


def test_fcfp4_bit_vectors_length():
    fps = fcfp4_bit_vectors([ETHANOL, ASPIRIN])
    assert len(fps) == 2


def test_fcfp4_bit_vectors_are_bitvects():
    fps = fcfp4_bit_vectors([ETHANOL])
    assert isinstance(fps[0], DataStructs.cDataStructs.ExplicitBitVect)
    assert fps[0].GetNumBits() == 1024


def test_fcfp4_bit_vectors_invalid_smiles_raises():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        fcfp4_bit_vectors(["not_valid"])


def test_fcfp4_bit_vectors_usable_with_bulk_similarity():
    fps = fcfp4_bit_vectors([ETHANOL, ASPIRIN])
    sims = DataStructs.BulkDiceSimilarity(fps[0], fps)
    assert len(sims) == 2
    assert sims[0] == pytest.approx(1.0)


def test_fcfp4_bit_vectors_use_features_false_gives_ecfp4_and_differs():
    ecfp4_fps = fcfp4_bit_vectors([ASPIRIN], use_features=False)
    fcfp4_fps = fcfp4_bit_vectors([ASPIRIN], use_features=True)
    assert ecfp4_fps[0].ToBitString() != fcfp4_fps[0].ToBitString()


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

"""Sanity tests for src/preprocessing.py."""

from rdkit import Chem
from src.preprocessing import standardize


CHARGED = "[NH4+]"           # simple charged molecule
SALT = "CC(=O)O.[Na+]"      # salt — has fragment (dot in SMILES)
ETHANOL = "CCO"


def test_standardize_returns_mol():
    mol = Chem.MolFromSmiles(ETHANOL)
    result = standardize(mol)
    assert result is not None


def test_standardize_removes_charge():
    mol = Chem.MolFromSmiles(CHARGED)
    result = standardize(mol)
    smi = Chem.MolToSmiles(result)
    assert "+" not in smi and "-" not in smi


def test_standardize_takes_largest_fragment():
    mol = Chem.MolFromSmiles(SALT)
    result = standardize(mol)
    smi = Chem.MolToSmiles(result)
    assert "." not in smi


def test_standardize_neutral_molecule_unchanged_shape():
    mol = Chem.MolFromSmiles(ETHANOL)
    result = standardize(mol)
    assert result.GetNumAtoms() == mol.GetNumAtoms()

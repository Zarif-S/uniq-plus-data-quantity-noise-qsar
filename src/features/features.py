"""Molecular featurization utilities for UNIQ+ QSAR experiments."""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdFingerprintGenerator


def morgan_fingerprints(smiles_list, radius=2, n_bits=1024, use_features=True):
    """Return (N, n_bits) numpy array of Morgan fingerprints for a list of SMILES.

    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.
    Defaults (radius=2, n_bits=1024, use_features=True) match the Fang et al. (2023) FCFP4 setup.
    use_features=True → FCFP (pharmacophoric atom invariants); False → ECFP (atomic number invariants).
    """
    if use_features:
        atom_inv = rdFingerprintGenerator.GetMorganFeatureAtomInvGen()
        morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits, atomInvariantsGenerator=atom_inv)
    else:
        morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        fps.append(np.array(morgan_gen.GetFingerprint(mol)))
    return np.array(fps)


def rdkit_descriptors(smiles_list):
    """Return DataFrame of RDKit 2D descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds).

    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.
    """
    records = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        records.append({
            "MW": Descriptors.MolWt(mol),
            "LogP": Descriptors.MolLogP(mol),
            "TPSA": rdMolDescriptors.CalcTPSA(mol),
            "HBD": rdMolDescriptors.CalcNumHBD(mol),
            "HBA": rdMolDescriptors.CalcNumHBA(mol),
            "RotBonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        })
    return pd.DataFrame(records)


def rdkit_2d_features(smiles_list):
    """Return (N, 200) normalized RDKit 2D descriptor array via descriptastorus."""
    from descriptastorus.descriptors import rdNormalizedDescriptors
    import warnings

    generator = rdNormalizedDescriptors.RDKit2DNormalized()
    features = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        result = generator.process(smi)
        if result is None:
            raise ValueError(f"Descriptor computation failed for SMILES: {smi!r}")
        vals = np.array(result[1:], dtype=float)  # first element is success flag
        if np.any(np.isnan(vals)):
            n_nan = int(np.sum(np.isnan(vals)))
            warnings.warn(f"{n_nan} NaN descriptor(s) for {smi!r}, replacing with 0.0")
            vals = np.nan_to_num(vals, nan=0.0)
        features.append(vals)
    return np.array(features)

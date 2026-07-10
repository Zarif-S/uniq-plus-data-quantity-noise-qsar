"""Molecular featurization utilities for UNIQ+ QSAR experiments."""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdFingerprintGenerator


def morgan_fingerprints(smiles_list, radius=2, n_bits=2048):
    """Return (N, n_bits) numpy array of Morgan fingerprints for a list of SMILES.

    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.
    Defaults (radius=2, n_bits=2048) are fixed ECFP4 project constants.
    """
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

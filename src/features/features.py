"""Molecular featurization utilities for UNIQ+ QSAR experiments."""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem


def morgan_fingerprints(smiles_list, radius=2, n_bits=1024):
    """Return (N, n_bits) numpy array of FCFP4 fingerprints for a list of SMILES.

    Uses AllChem.GetMorganFingerprintAsBitVect with useFeatures=True — matches paper code exactly.
    Defaults (radius=2, n_bits=1024) match Fang et al. (2023) FCFP4 setup.
    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.
    """
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        fps.append(np.array(AllChem.GetMorganFingerprintAsBitVect(mol, radius, useFeatures=True, nBits=n_bits)))
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


def rdmoldes(mols):
    """Return (N, 316) numpy array of the paper's hand-picked rdMolDes descriptor set.

    Matches Fang et al. (2023) ADME_ML_public.py MDlist exactly.
    316 features: 44 scalar descriptors + 272 from 6 vector descriptors
    (PEOE_VSA_=14, SMR_VSA_=10, SlogP_VSA_=12, MQNs_=42, CrippenDescriptors=2, AUTOCORR2D=192).

    Args:
        mols: list of RDKit mol objects. Mols must already have a conformer (loaded from SDF)
              for the 9 geometry-dependent descriptors (CalcPMI1/2/3, CalcAsphericity, etc.)
              to return meaningful values. Raises ValueError for any None mol.
    """
    records = []
    for mol in mols:
        if mol is None:
            raise ValueError("None mol object encountered — all mols must be valid RDKit mol objects")
        row = [
        # 44 scalar descriptors
            rdMolDescriptors.CalcTPSA(mol),
            rdMolDescriptors.CalcFractionCSP3(mol),
            rdMolDescriptors.CalcNumAliphaticCarbocycles(mol),
            rdMolDescriptors.CalcNumAliphaticHeterocycles(mol),
            rdMolDescriptors.CalcNumAliphaticRings(mol),
            rdMolDescriptors.CalcNumAmideBonds(mol),
            rdMolDescriptors.CalcNumAromaticCarbocycles(mol),
            rdMolDescriptors.CalcNumAromaticHeterocycles(mol),
            rdMolDescriptors.CalcNumAromaticRings(mol),
            rdMolDescriptors.CalcNumLipinskiHBA(mol),
            rdMolDescriptors.CalcNumLipinskiHBD(mol),
            rdMolDescriptors.CalcNumHeteroatoms(mol),
            rdMolDescriptors.CalcNumRings(mol),
            rdMolDescriptors.CalcNumRotatableBonds(mol),
            rdMolDescriptors.CalcNumSaturatedCarbocycles(mol),
            rdMolDescriptors.CalcNumSaturatedHeterocycles(mol),
            rdMolDescriptors.CalcNumSaturatedRings(mol),
            rdMolDescriptors.CalcHallKierAlpha(mol),
            rdMolDescriptors.CalcKappa1(mol),
            rdMolDescriptors.CalcKappa2(mol),
            rdMolDescriptors.CalcKappa3(mol),
            rdMolDescriptors.CalcChi0n(mol),
            rdMolDescriptors.CalcChi0v(mol),
            rdMolDescriptors.CalcChi1n(mol),
            rdMolDescriptors.CalcChi1v(mol),
            rdMolDescriptors.CalcChi2n(mol),
            rdMolDescriptors.CalcChi2v(mol),
            rdMolDescriptors.CalcChi3n(mol),
            rdMolDescriptors.CalcChi3v(mol),
            rdMolDescriptors.CalcChi4n(mol),
            rdMolDescriptors.CalcChi4v(mol),
            rdMolDescriptors.CalcAsphericity(mol), #3d
            rdMolDescriptors.CalcEccentricity(mol), #3d
            rdMolDescriptors.CalcInertialShapeFactor(mol), #3d
            rdMolDescriptors.CalcExactMolWt(mol),
            rdMolDescriptors.CalcPBF(mol), #3d
            rdMolDescriptors.CalcPMI1(mol), #3d
            rdMolDescriptors.CalcPMI2(mol), #3d
            rdMolDescriptors.CalcPMI3(mol), #3d
            rdMolDescriptors.CalcRadiusOfGyration(mol), #3d
            rdMolDescriptors.CalcSpherocityIndex(mol),  #3d
            rdMolDescriptors.CalcLabuteASA(mol), #3d        
            rdMolDescriptors.CalcNPR1(mol), #3d
            rdMolDescriptors.CalcNPR2(mol), #3d
        ]
        # 272 descriptors from 6 vector descriptors
        # Vector descriptors: PEOE_VSA_(14), SMR_VSA_(10), SlogP_VSA_(12),
        # MQNs_(42), CrippenDescriptors(2), AUTOCORR2D(192) = 272 values
        row.extend(rdMolDescriptors.PEOE_VSA_(mol))
        row.extend(rdMolDescriptors.SMR_VSA_(mol))
        row.extend(rdMolDescriptors.SlogP_VSA_(mol))
        row.extend(rdMolDescriptors.MQNs_(mol))
        row.extend(rdMolDescriptors.CalcCrippenDescriptors(mol))
        row.extend(rdMolDescriptors.CalcAUTOCORR2D(mol))
        records.append(row)
    return np.array(records, dtype=np.float64)


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

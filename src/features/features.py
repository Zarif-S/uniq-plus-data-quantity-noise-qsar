"""Molecular featurization utilities for UNIQ+ QSAR experiments."""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem


def morgan_fingerprints(smiles_list, radius=2, n_bits=1024, use_features=True):
    """Return (N, n_bits) numpy array of Morgan fingerprints for a list of SMILES.

    use_features=True (default) gives FCFP4 — matches paper code exactly and remains the fixed
    featurizer for the primary modelling pipeline. use_features=False gives ECFP4, added as an
    extra modelling representation for the §5.3b representation-comparison study (see DECISIONS.md:
    ECFP4 promoted from comparison-only to a modelling representation).
    Defaults (radius=2, n_bits=1024) match Fang et al. (2023) FCFP4 setup.
    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.

    Does NOT standardize input mols — caller is responsible for passing already-standardized
    SMILES (e.g. via src.preprocessing.standardize) if standardization matters for the study.
    """
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        fps.append(np.array(AllChem.GetMorganFingerprintAsBitVect(mol, radius, useFeatures=use_features, nBits=n_bits)))
    return np.array(fps)


def fcfp4_bit_vectors(smiles_list, radius=2, n_bits=1024, use_features=True):
    """Return list of RDKit ExplicitBitVect Morgan fingerprints for pairwise similarity use.

    Unlike morgan_fingerprints (numpy array, for ML features), this returns raw bit vectors
    for use with DataStructs.BulkDiceSimilarity / BulkTanimotoSimilarity.
    Despite the name (project default is FCFP4, use_features=True), passing use_features=False
    gives ECFP4 instead — same RDKit call, only the invariant seeding differs. ECFP4 is
    comparison-only (see DECISIONS.md); FCFP4 remains the fixed featurizer for modelling.
    Raises ValueError for any invalid SMILES.
    """
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        fps.append(rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits, useFeatures=use_features))
    return fps


def rdkit_descriptors(smiles_list):
    """Return DataFrame of RDKit 2D descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds).

    Raises ValueError for any invalid SMILES — pre-validate with smiles_validity_report.

    Does NOT standardize input mols — caller is responsible for passing already-standardized
    SMILES (e.g. via src.preprocessing.standardize) if standardization matters for the study.
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


def rdkit_2d_features(smiles_list, normalized=True):
    """Return (N, 200) RDKit 2D descriptor array via descriptastorus.

    normalized=True (default): CDF-normalized to [0,1] via RDKit2DNormalized (paper-faithful; MPNN3).
    normalized=False: raw un-normalized RDKit2D values (MPNN4 feature-count control) — SAME 200
    descriptors, no CDF, so values are unbounded and can be inf. Both variants replace NaN with 0.0;
    the raw variant additionally clamps ±inf to the largest finite float (nan_to_num default) so the
    rank-based QuantileTransformer downstream keeps their extreme ordering rather than erroring.
    """
    from descriptastorus.descriptors import rdNormalizedDescriptors, rdDescriptors
    import warnings

    generator = rdNormalizedDescriptors.RDKit2DNormalized() if normalized else rdDescriptors.RDKit2D()
    features = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(str(smi)) if pd.notna(smi) else None
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        result = generator.process(smi)
        if result is None:
            raise ValueError(f"Descriptor computation failed for SMILES: {smi!r}")
        vals = np.array(result[1:], dtype=float)  # first element is success flag
        if not np.all(np.isfinite(vals)):
            n_bad = int(np.sum(~np.isfinite(vals)))
            warnings.warn(f"{n_bad} non-finite descriptor(s) for {smi!r}, replacing NaN->0.0 / inf->max-finite")
            vals = np.nan_to_num(vals, nan=0.0)  # posinf/neginf default to largest finite float
        features.append(vals)
    return np.array(features)

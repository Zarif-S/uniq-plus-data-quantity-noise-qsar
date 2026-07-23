"""Molecule standardization utilities for UNIQ+ QSAR experiments."""

from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize

# Instantiate once at module level — avoids re-initializing (and re-logging) for every molecule
_UNCHARGER = rdMolStandardize.Uncharger()
_TAUTOMER_ENUMERATOR = rdMolStandardize.TautomerEnumerator()


def standardize(mol):
    """Standardize an RDKit mol object to match Fang et al. (2023) preprocessing.

    Applies four steps in order, matching ADME_ML_public.py standardize() exactly:
      1. Cleanup      — remove Hs, disconnect metal atoms, normalize bonds, reionize
      2. FragmentParent — if multiple fragments (salts etc.), keep the largest organic parent
      3. Uncharge     — neutralize charges where possible
      4. TautomerEnumerator.Canonicalize — pick a canonical tautomer

    Falls back to SMILES round-trip if step 1-4 raise, then returns mol unchanged if that
    also fails. Both fallbacks log a warning so failures are visible rather than silent.
    """
    import warnings
    try:
        # Step 1: remove Hs, disconnect metal atoms, normalize the molecule, reionize
        clean_mol = rdMolStandardize.Cleanup(mol)
        # Step 2: if many fragments, get the parent (the actual mol we are interested in)
        parent_clean_mol = rdMolStandardize.FragmentParent(clean_mol)
        # Step 3: try to neutralize molecule
        uncharged_parent_clean_mol = _UNCHARGER.uncharge(parent_clean_mol)
        # Step 4: try to canonicalize tautomers
        mol_final = _TAUTOMER_ENUMERATOR.Canonicalize(uncharged_parent_clean_mol)
    except Exception as e:
        warnings.warn(f"standardize() failed ({e}), falling back to SMILES round-trip")
        try:
            mol_final = Chem.MolFromSmiles(Chem.MolToSmiles(mol))
        except Exception as e2:
            warnings.warn(f"SMILES round-trip also failed ({e2}), returning mol unchanged")
            mol_final = mol
    return mol_final

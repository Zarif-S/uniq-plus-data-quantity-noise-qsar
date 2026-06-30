# Skills Sources

## Scientific Agent Skills
**Repo**: https://github.com/K-Dense-AI/scientific-agent-skills

148+ ready-to-use scientific skills covering drug discovery, bioinformatics, ML, clinical research, and more.
Compatible with Claude Code — copy any `SKILL.md` from the repo into `.claude/commands/<skill-name>.md` to add it.

### Currently installed (Drug Discovery & Medicinal Chemistry)
| Skill | Command | Description |
|---|---|---|
| RDKit | `/rdkit` | Core cheminformatics — SMILES, descriptors, fingerprints, reactions |
| MedChem | `/medchem` | Drug-likeness filters, PAINS, structural alerts |
| Datamol | `/datamol` | Simplified RDKit wrapper for standard workflows |
| DeepChem | `/deepchem` | ML for property prediction (ADMET, toxicity) |
| Molfeat | `/molfeat` | 100+ molecular featurizers for ML/QSAR |
| DiffDock | `/diffdock` | Protein-ligand molecular docking |
| Molecular Dynamics | `/molecular-dynamics` | MD simulations with OpenMM & MDAnalysis |
| TorchDrug | `/torchdrug` | PyTorch GNNs for drug discovery |
| PyTDC | `/pytdc` | Therapeutics Data Commons datasets & benchmarks |

### Installing new skills
```bash
# Browse available skills at the repo above, then:
cp <downloaded-SKILL.md> .claude/commands/<skill-name>.md
```

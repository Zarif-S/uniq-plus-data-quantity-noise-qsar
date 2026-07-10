# Skills Sources

## Scientific Agent Skills
**Repo**: https://github.com/K-Dense-AI/scientific-agent-skills

148+ ready-to-use scientific skills covering drug discovery, bioinformatics, ML, clinical research, and more.
Compatible with Claude Code — copy any `SKILL.md` from the repo into `.claude/commands/<skill-name>.md` to add it.

> **Verification note**: Before marking a skill as installed, confirm the `.md` file exists in `.claude/commands/`. A skill listed here but missing its file cannot be invoked. Run `ls .claude/commands/` to check.

### Currently installed (Drug Discovery & Medicinal Chemistry)

The skills below are available system-wide (visible in the Claude Code Skill tool) but their source `.md` files are **not present** in `.claude/commands/` of this project. They work via the user-level skill installation, not via local project files.

| Skill | Command | Local .md file | Description |
|---|---|---|---|
| RDKit | `/rdkit` | missing | Core cheminformatics — SMILES, descriptors, fingerprints, reactions |
| MedChem | `/medchem` | missing | Drug-likeness filters, PAINS, structural alerts |
| Datamol | `/datamol` | missing | Simplified RDKit wrapper for standard workflows |
| DeepChem | `/deepchem` | missing | ML for property prediction (ADMET, toxicity) |
| Molfeat | `/molfeat` | missing | 100+ molecular featurizers for ML/QSAR |
| DiffDock | `/diffdock` | missing | Protein-ligand molecular docking |
| Molecular Dynamics | `/molecular-dynamics` | missing | MD simulations with OpenMM & MDAnalysis |
| TorchDrug | `/torchdrug` | missing | PyTorch GNNs for drug discovery |
| PyTDC | `/pytdc` | missing | Therapeutics Data Commons datasets & benchmarks |

To install local copies (so the skills are project-portable and not dependent on user-level config):

### Installing skill files locally
```bash
# Browse available skills at the repo above, then for each skill:
cp <downloaded-SKILL.md> .claude/commands/<skill-name>.md

# Example for RDKit:
# Download rdkit SKILL.md from https://github.com/K-Dense-AI/scientific-agent-skills
cp rdkit-SKILL.md .claude/commands/rdkit.md
```

> **MANUAL STEP — Zarif to action**
> Download each listed skill's `SKILL.md` from `https://github.com/K-Dense-AI/scientific-agent-skills` and copy it to `.claude/commands/<skill-name>.md`. Then verify all files are present:
> ```bash
> ls .claude/commands/*.md
> ```
> Update the "Local .md file" column above from `missing` to `present` once done.

> **WARNING**: Do not mark a skill as installed until the `.md` file physically exists in `.claude/commands/`. Listing it without the file means the `/skill` command will silently fail.

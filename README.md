# Predicting ADME Properties using Machine Learning

*(Originally titled: Understanding the Effects of Data Quantity and Label Noise on Machine Learning Models in Drug Discovery)*

Reproduces and stress-tests the claims of Fang et al. (2023) — a Biogen study validating ML algorithms for ADME (Absorption, Distribution, Metabolism, Excretion) prediction — using their publicly released dataset in place of the confidential in-house one the paper was built on. Extends into feature selection, statistical significance testing of model comparisons, and (as a secondary strand) how training-set size and label noise affect model performance.

---

## What this project does

1. **Reproduces the paper's claims** on the public dataset (3,521 compounds vs. the original 22,822 confidential compounds) — algorithm ranking (non-RF > RF baseline), the role of molecular representation vs. algorithm choice, and MAE-vs-similarity trends — and reports where the claims held, weakened, or reversed on the smaller public set.
2. **Tests sensitivity of those claims to methodology** — e.g. the paper describes "FCFP4" as radius 4, but by definition FCFP4 is radius 2/diameter 4; source code confirms radius 2 was actually used. Where a claim changes under reasonable methodological variation, that fragility is itself a finding.
3. **Quantifies statistical significance** of pairwise model comparisons via repeated k-fold CV (k=5, 3 repeats) + paired one-way ANOVA + Tukey HSD, visualised as significance heatmaps per endpoint.
4. **Reduces 50 RDKit descriptors to a minimal informative subset** via a staged pipeline (variance filter → PCA/mutual information → CCA redundancy pruning → VIF pruning → LightGBM recursive feature elimination), finding 2 descriptors (PEOE_VSA, SlogP_VSA) retain 82% of the 48-descriptor baseline's predictive performance.
5. **Data-quantity and noise experiments** (originally the project's central strand, deprioritised as the reproduction work expanded, then revisited later): learning curves across training-set fractions, and label-noise injection (Gaussian, systematic bias, gross errors), to understand how classical vs. deep models degrade under scarce or imperfect data.

---

## Dataset

| Dataset | Compounds | Endpoints | Source |
|---------|-----------|-----------|--------|
| ADME public set | 3,521 (3,087 after cleaning for modelling) | HLM/RLM clearance, MDR1 efflux, solubility, PPB (human/rat) | Fang et al. (2023), public |

Fang, C., Wang, Y., Grater, R., Kapadnis, S., Black, C., Trapa, P. and Sciabola, S. (2023) "Prospective validation of machine learning algorithms for absorption, distribution, metabolism, and excretion prediction: An industrial perspective," *Journal of Chemical Information and Modeling*, 63(11), pp. 3263–3274. DOI: [10.1021/acs.jcim.3c00160](https://doi.org/10.1021/acs.jcim.3c00160).

---

## Setup

Requires Python 3.11 and [uv](https://github.com/astral-sh/uv).

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install pinned environment
git clone <repository-url>
cd predicting-adme-ml
uv sync

# Activate and launch
source .venv/bin/activate
jupyter lab
```

No environment variables required — all data is open source and loaded from local files.

---

## Project Structure

```
predicting-adme-ml/
├── notebooks/           # EDA, paper recreation, and experiment notebooks (numbered: 01_, 03_, 04_, ...)
├── src/                 # Reusable modules imported by notebooks (features, models, cleaning, noise, ...)
├── data/
│   ├── raw/              # Original datasets, never modified
│   └── processed/        # Cleaned/featurised data (large intermediate files are gitignored — see notebooks to regenerate)
├── tests/                # Sanity tests for src/ modules
└── pyproject.toml        # Dependencies (managed via uv)
```

---

## Notebooks

| Notebook | Content |
|---|---|
| `01.5_adme_biogen_public_recreation.ipynb` | Paper recreation: EDA, preprocessing, featurization, 9-model baseline + tuned evaluation |
| `01.6_adme_paper_recreation_results.ipynb` | Paper recreation results tables/figures, claim-by-claim comparison, significance heatmaps |
| `01.7_adme_mmp_analysis.ipynb` | Matched molecular pair analysis |
| `01.8_feature_selection.ipynb` | Staged RDKit descriptor selection pipeline (50 → 2 descriptors) |
| `01.9_stereochemistry_analysis.ipynb` | Per-endpoint stereocentre / unassigned-stereo analysis |
| `03_adme_data_quantity.ipynb` | Data-quantity (learning curve) experiment |
| `04_adme_noise.ipynb` | Label noise injection experiment |
| `05_dataset_size_comparison_viz.ipynb` | Combined data-quantity/noise visualisation |

Superseded early-stage notebooks are kept in `notebooks/archive/` for reference.

---

## Running Tests

```bash
uv run pytest tests/
```

---

## Benchmarks

`benchmarks/` contains standalone A/B scripts used to make infrastructure decisions (CPU vs MPS device choice, cross-validation parallelism layout) — not part of the research pipeline itself. They run from any working directory:

```bash
python benchmarks/bench_fcnn_device.py [epochs]
python benchmarks/bench_parallelism.py --n-jobs-model 1 --n-jobs-cv 3 --label A
```

Both require `data/processed/section4_splits.pkl`, which is a large intermediate file regenerated by `01.5_adme_biogen_public_recreation.ipynb` (not tracked in git — run the notebook first).

---

## Documentation

- [PROJECT_PLAN.md](PROJECT_PLAN.md) — final project status
- [DECISIONS.md](DECISIONS.md) — architectural decision records (ADRs)
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) — process and technical lessons
- [CHANGELOG.md](CHANGELOG.md) — change history

---

## Built With

This project used the [Strategic Agentic Coding Framework](https://github.com/Zarif-S/agentic-coding-framework) for documentation structure and AI-agent workflow — a hierarchical doc system (CLAUDE.md / PROJECT_PLAN.md / DECISIONS.md) that keeps AI coding assistants context-efficient across a project. See [`docs/agentic-framework-guide.md`](docs/agentic-framework-guide.md) for a local quickstart guide.

---

## Acknowledgments

An 8-week academic research project with [OPIG](https://opig.stats.ox.ac.uk/) (Oxford Protein Informatics Group), part of the Oxford UNIQ+ summer research programme. Supervised by Fergus Imrie, Acer Blake, and Charlotte Deane MBE.

---

**Status**: Project complete | **Maintainer**: Zarif

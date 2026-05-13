# Benchmark Saturation

Companion code for the paper *When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation* ([arXiv:2602.16763](https://arxiv.org/abs/2602.16763)).

This repository provides a research framework for systematically characterizing the complexity and saturation dynamics of AI benchmarks over time. It tracks how model performance evolves on benchmarks (HELM Classic, HuggingFace Open LLM v2), computes a statistical saturation index (S_index), and produces the time-series trajectories analyzed in the paper.

## Objectives

### 1. Characterize benchmark complexity
- Curate and measure **high-level properties** (domain, task type, data generation methodology, modality, curation process, overlap with model training data).
- Measure **fine-grained properties** (semantic and literal diversity, content coverage, prompt variability, modality composition).
- Use automated metadata parsing, manual annotation, and targeted content analysis, informed by frameworks such as BetterBench.

### 2. Analyze benchmark saturation dynamics
- Study why some benchmarks (e.g., MATH, ARC-AGI) remain challenging while others are rapidly "solved."
- Track time-series model performance and leaderboard progress to identify architecture-specific gains and saturation points.
- Cluster benchmarks into "fast" and "slow" saturation categories based on performance trajectories.
- Analyze benchmark properties that may explain these patterns.

## Install

Requires Python 3.10 or newer. Install both requirement files:

```bash
pip install -r analyzer/requirements.txt   # core analyzer
pip install -r scripts/requirements.txt    # plotting / paper-figure scripts
```

Some leaderboard data is stored via Git LFS — fetch it after cloning:

```bash
git lfs pull
```

Copy the env template and add your own keys:

```bash
cp .env.example .env
# edit .env and set SEMANTIC_SCHOLAR_API_KEY (optional, used for citation counts)
```

## Quickstart

Run all metrics for the HELM Classic leaderboard (BoolQ, HellaSwag, MMLU, NarrativeQA, NaturalQuestions, OpenBookQA, QuAC, TruthfulQA):

```bash
python3 -m analyzer.src.leaderboards.helm.run_metrics
# → metrics_output_helm_classic.csv
```

Run all metrics for the HuggingFace Open LLM v2 leaderboard (BBH, GPQA, MMLU-PRO, MUSR, IFEval, MATH):

```bash
python3 -m analyzer.src.leaderboards.hf_openllm_v2.run_metrics
# → metrics_output_hf_llm_v2.csv
# → results/saturation_trajectories/*.json
```

See [`analyzer/README.md`](analyzer/README.md) for the metric catalogue, the S_index formula, and instructions for adding new datasets or leaderboards.

## Reproducing the paper

See [REPRODUCE.md](REPRODUCE.md) for the mapping between scripts and the figures/tables reported in the paper.

## Repository layout

```
benchmark-saturation/
├── analyzer/                     # Metrics framework (Python package)
│   └── src/
│       ├── leaderboards/         # HELM Classic and HF Open LLM v2 implementations
│       ├── metrics/              # Static and dynamic metrics, S_index, temporal analysis
│       └── processing/           # Shared data-processing utilities
├── data/                         # Dataset metadata, leaderboard snapshots, manual annotations
├── results/                      # Generated CSVs and saturation trajectory JSONs
├── scripts/                      # Plotting scripts and paper-figure analysis
├── tests/                        # Test fixtures (placeholder)
└── website/                      # Web visualization (work in progress; not part of this release)
```

## Citation

If you use this code or the accompanying paper, please cite:

```bibtex
@misc{akhtar2026aibenchmarksplateausystematic,
      title={When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation},
      author={Mubashara Akhtar and Anka Reuel and Prajna Soni and Sanchit Ahuja and Pawan Sasanka Ammanamanchi and Ruchit Rawal and Vilém Zouhar and Srishti Yadav and Chenxi Whitehouse and Dayeon Ki and Jennifer Mickel and Leshem Choshen and Marek Šuppa and Jan Batzner and Jenny Chim and Jeba Sania and Yanan Long and Hossein A. Rahmani and Christina Knight and Yiyang Nan and Jyoutir Raj and Yu Fan and Shubham Singh and Subramanyam Sahoo and Eliya Habba and Usman Gohar and Siddhesh Pawar and Robert Scholz and Arjun Subramonian and Jingwei Ni and Mykel Kochenderfer and Sanmi Koyejo and Mrinmaya Sachan and Stella Biderman and Zeerak Talat and Avijit Ghosh and Irene Solaiman},
      year={2026},
      eprint={2602.16763},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2602.16763},
}
```

A `CITATION.cff` file is also provided at the repo root.

## License

This project is released under the [MIT License](LICENSE).

## Contact

Please open an issue on this repository for questions, bug reports, or reproducibility problems.

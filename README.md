# Benchmark Saturation

## Overview
Benchmark Saturation investigates how to systematically characterize the complexity and behavior of AI benchmarks over time to inform the design of more robust and meaningful benchmarks.

## Objectives

### 1. Characterize Benchmark Complexity

- Curate and measure **high-level properties** (domain, task type, data generation methodology, modality, curation process, overlap with model training data).
- Measure **fine-grained properties** (semantic and literal diversity, content coverage, prompt variability, modality composition).
- Use **automated metadata parsing**, **manual annotation**, and **targeted content analysis**, informed by frameworks such as BetterBench.

### 2. Analyze Benchmark Saturation Dynamics

- Study why some benchmarks (e.g., MATH, ARC-AGI) remain challenging while others are rapidly “solved.”
- Track **time-series model performance and leaderboard progress** to identify architecture-specific gains and saturation points.
- Cluster benchmarks into **“fast” and “slow” saturation categories** based on performance trajectories.
- Analyze benchmark properties to identify **characteristics that may explain these saturation patterns**.

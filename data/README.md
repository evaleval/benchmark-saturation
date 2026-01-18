# Benchmark Saturation – Manual Annotation Dataset

This dataset contains **manually annotated metadata and saturation measurements** for NLP/ML benchmarks. It is designed to study **when and how benchmarks lose their ability to distinguish state-of-the-art models**.

Each row corresponds to a **single benchmark** and combines:
- leaderboard statistics  
- uncertainty-aware saturation metrics  
- rich dataset and provenance information  


## Supported Analyses

The dataset supports analyses of:

- **Benchmark saturation** and score compression at the top of leaderboards  
- The relationship between **test set size**, **evaluation noise**, and **discriminative power**  
- **Dataset quality issues** (e.g., contamination, mislabeling) and their impact on saturation  
- Differences between **task types**, **metrics**, and **curation practices**

For each field in the dataset, a definition is provided in the **“Field Definitions”** tab.


## Structure

Each row represents **one benchmark**. Columns fall into four broad categories.

### 1. Benchmark Metadata
Basic identifying information, including:
- benchmark name  
- release date  
- task type  
- languages  
- availability (public vs. private)

### 2. Leaderboard & Saturation Statistics
(See Overleaf document, Section 2.2, for calculation details.)

Includes top-5 model scores and descriptive statistics:
- mean  
- standard deviation  
- range  

As well as uncertainty-aware quantities:
- **SE_delta**: standard error of the score difference between the top-1 and top-5 models  
- **R_norm**: normalized score gap relative to evaluation uncertainty  
- **Saturation Index**: continuous measure in \([0,1]\), where higher values indicate stronger saturation  
- **Saturation Index (interpreted)**: categorical interpretation (Very low → Very high)

### 3. Saturation Timing & Model Coverage
Information on:
- when saturation occurred (relative to benchmark release)  
- whether recent frontier models have been evaluated  
- supporting metadata (top-5 model names and scores)

### 4. Dataset Provenance & Quality Signals
Manual annotations covering:
- dataset curation methods  
- known issues (e.g., contamination, biases, mislabeling)  
- input/output formats  
- literal diversity  
- metrics used  
- references to follow-up studies  


## Saturation Index

The **Saturation Index** quantifies how indistinguishable top-performing models are once **evaluation uncertainty** is taken into account.

- Values close to **0** indicate large, reliable performance gaps (**low saturation**)  
- Values close to **1** indicate tight clustering within noise (**high saturation**)  

An interpreted categorical label (**Very low, Low, Moderate, High, Very high**) is provided for ease of analysis and reporting.


## Intended Use

This dataset is intended for:

- Meta-analysis of **benchmark health and longevity**  
- Studying **model-level vs. task-level saturation**  
- Comparing saturation patterns across **task types**, **metrics**, and **domains**  
- Supporting principled discussions about **when benchmarks should be revised, extended, or retired**


## Notes

- Scores are reported as published on leaderboards or in model evaluation reports  
- Saturation metrics are computed using an **uncertainty-aware formulation** that accounts for test set size  
- Manual annotations reflect best-effort synthesis of papers, leaderboards, and follow-up analyses at the time of collection  


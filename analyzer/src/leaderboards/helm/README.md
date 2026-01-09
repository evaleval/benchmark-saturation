# HELM Leaderboard Implementation

This folder contains the implementation of HELM (Holistic Evaluation of Language Models) benchmark datasets and leaderboard orchestration.

## Overview

The HELM leaderboard includes datasets from three benchmark categories:
- **HELM Lite** - Core evaluation datasets
- **HELM Capabilities** - Advanced capability testing
- **HELM Finance** - Financial domain evaluation

## Structure

### Dataset Classes (10 files)

All dataset classes follow the same pattern as HF Open LLM v2, inheriting from the `Dataset` base class:

1. **`banking77.py`** - Banking customer service intent classification
   - HF Dataset: `mteb/banking77`
   - Benchmark: HELM Finance
   - Paper: https://arxiv.org/abs/2003.04807

2. **`financebench.py`** - Financial question answering benchmark
   - HF Dataset: `PatronusAI/financebench`
   - Benchmark: HELM Finance
   - Paper: https://arxiv.org/abs/2311.11944

3. **`finqa.py`** - Financial numerical reasoning
   - HF Dataset: `ibm-research/finqa`
   - Benchmark: HELM Finance
   - Note: Marked as missing in metadata extraction but implemented for completeness

4. **`legalbench.py`** - Legal reasoning and comprehension
   - HF Dataset: `nguha/legalbench`
   - Benchmark: HELM Lite
   - Paper: https://arxiv.org/abs/2308.11462

5. **`med_qa.py`** - Medical question answering
   - HF Dataset: `bigbio/med_qa`
   - Benchmark: HELM Lite

6. **`narrativeqa.py`** - Reading comprehension on narratives
   - HF Dataset: `deepmind/narrativeqa`
   - Benchmark: HELM Lite
   - Paper: https://arxiv.org/abs/1712.07040

7. **`omni_math.py`** - Olympiad-level mathematics
   - HF Dataset: `KbsdJames/Omni-MATH`
   - Benchmark: HELM Capabilities
   - Paper: https://arxiv.org/abs/2410.07985
   - Note: Renamed from `omni-math.py` for Python import compatibility

8. **`openbookqa.py`** - Open book question answering
   - HF Dataset: `allenai/openbookqa`
   - Benchmark: HELM Lite

9. **`wildbench.py`** - Real-world challenging tasks
   - HF Dataset: `allenai/WildBench`
   - Benchmark: HELM Capabilities
   - Paper: https://arxiv.org/abs/2406.04770

10. **`wmt14.py`** - Machine translation benchmark
    - HF Dataset: `wmt/wmt14`
    - Benchmark: HELM Lite
    - Multiple language pairs: cs-en, de-en, fr-en, hi-en, ru-en

### Orchestration Files

- **`benchmark.py`** - `HELMLeaderboard` class that manages all HELM datasets
  - Inherits from `Leaderboard` base class
  - Implements `refresh()` and `compute_rankings()` methods
  - Aggregates dataset information across all HELM benchmarks

- **`run_metrics.py`** - Main runner script that:
  - Initializes all 9 HELM Classic datasets with their metadata
  - Loads metadata from `data/all_datasets.json` (same as hf_openllm_v2)
  - Adds datasets to the HELM leaderboard
  - Runs all static and dynamic metrics on each dataset
  - Exports results to CSV

- **`__init__.py`** - Empty file that makes this directory a Python package

## Dataset Class Structure

Each dataset class implements:

```python
class ExampleDataset(Dataset):
    def __init__(self, name, paper_url, dataset_url, hf_dataset_id, **kwargs):
        # Initialize with metadata
        
    def refresh(self) -> None:
        # Refresh dataset (currently no-op)
        
    def download(self):
        # Load metadata from JSON file
        
    def process(self, data: Dict[str, Any]):
        # Process metadata and create DataFrame with:
        # - paper_url
        # - dataset_url
        # - language
        # - is_public
        # - modality
        # - data_created
        # - leaderboard_detail
        # - total_samples
        # - task_categories
```

## Metrics

### Static Metrics
The implementation uses existing static metrics from `analyzer/src/metrics/static/`:

- **`TotalLenDatasetMetric`** - Total number of samples in the dataset
- **`ModalityMetric`** - Dataset modality (e.g., text, image)
- **`LanguageMetric`** - Language(s) used in the dataset
- **`IsPublicMetric`** - Whether the dataset is publicly available
- **`LeaderboardDetailMetric`** - Which HELM benchmark the dataset belongs to
- **`TaskCategoryMetric`** - Task categories/types

### Dynamic Metrics
The implementation also tracks time-varying metrics from `analyzer/src/metrics/dynamic/`:

- **`DatasetDownloadsMetric`** - Number of downloads from Hugging Face (tracks popularity)
- **`DatasetLikesMetric`** - Number of likes/stars (community appreciation)
- **`DatasetFreshnessMetric`** - Last modification date (dataset maintenance)
- **`TrendingScoreMetric`** - Trending score (popularity velocity)

See `analyzer/src/metrics/dynamic/HELM_DYNAMIC_METRICS.md` for detailed documentation on dynamic metrics.

## Usage

To run all HELM metrics:

```bash
python3 -m analyzer.src.leaderboards.helm.run_metrics
```

This will:
1. Initialize all 9 HELM Classic datasets
2. Load metadata from `data/all_datasets.json` (same source as hf_openllm_v2)
3. Process each dataset and extract metadata
4. Run all static and dynamic metrics on each dataset
5. Export results to `metrics_output_helm_classic.csv`

## Metadata Source

Dataset metadata is extracted from:
- **Source**: `data/all_datasets.json` (shared with hf_openllm_v2)
- **Generated by**: `data/parse_yaml_files_to_json.py`
- **Original data**: `data/split_yaml/all_dataset_info_part*.yaml` files

The metadata extraction script scans YAML exports and collects information for all datasets where the benchmark column mentions "HELM" (Lite, Capabilities, or Finance).

## Dependencies

Required packages (from `analyzer/requirements.txt`):
- `pandas>=1.3.0`
- `datasets==3.2.0`

## Implementation Notes

1. **File naming**: `omni-math.py` was renamed to `omni_math.py` because Python module names cannot contain hyphens
2. **Error handling**: All dataset classes include try-except blocks for loading datasets, with fallback to metadata values
3. **Configuration handling**: Datasets with multiple configurations (e.g., `legalbench`, `openbookqa`, `wmt14`) handle the primary configuration
4. **Leaderboard categories**: Each dataset is tagged with its HELM category (Lite, Capabilities, or Finance) via the `leaderboard_detail` field



# HELM Classic Leaderboard Implementation

This folder contains the implementation of HELM Classic (Holistic Evaluation of Language Models - Classic benchmark scenarios) datasets and leaderboard orchestration.

## Overview

The HELM Classic leaderboard includes 9 core evaluation scenarios from the original HELM benchmark:
- **MMLU** (Massive Multitask Language Understanding)
- **BoolQ** (Boolean Questions)
- **NarrativeQA** (Reading comprehension on narratives)
- **NaturalQuestions** (Closed-book and open-book question answering)
- **QuAC** (Question Answering in Context)
- **HellaSwag** (Commonsense reasoning)
- **OpenBookQA** (Open book question answering)
- **TruthfulQA** (Truthful question answering)

## Structure

### Dataset Classes (9 files)

All dataset classes follow the same pattern as HF Open LLM v2, inheriting from the `Dataset` base class:

1. **`boolq.py`** - Boolean question answering
   - HF Dataset: `google/boolq`
   - Paper: https://arxiv.org/abs/1905.10044

2. **`hellaswag.py`** - Commonsense reasoning
   - HF Dataset: `Rowan/hellaswag`
   - Paper: https://arxiv.org/abs/1905.07830

3. **`mmlu.py`** - Massive Multitask Language Understanding
   - HF Dataset: `cais/mmlu`
   - Paper: https://arxiv.org/abs/2009.03300

4. **`narrativeqa.py`** - Reading comprehension on narratives
   - HF Dataset: `deepmind/narrativeqa`
   - Paper: https://arxiv.org/abs/1712.07040

5. **`naturalquestions.py`** - Natural question answering (closed-book and open-book)
   - HF Dataset: `google-research-datasets/natural_questions`
   - Paper: https://arxiv.org/abs/1901.08634

6. **`openbookqa.py`** - Open book question answering
   - HF Dataset: `allenai/openbookqa`
   - Paper: https://arxiv.org/abs/1809.02789

7. **`quac.py`** - Question Answering in Context
   - HF Dataset: `allenai/quac`
   - Paper: https://arxiv.org/abs/1808.07036

8. **`truthfulqa.py`** - Truthful question answering
   - HF Dataset: `domenicrosati/TruthfulQA`
   - Paper: https://arxiv.org/abs/2109.07958

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
- **`CreatedAtMetric`** - Dataset creation date

### Dynamic Metrics
The implementation tracks time-varying metrics from `analyzer/src/metrics/dynamic/`:

- **`DatasetDownloadsMetric`** - Number of downloads from Hugging Face (tracks popularity)
- **`DatasetLikesMetric`** - Number of likes/stars (community appreciation)
- **`DatasetFreshnessMetric`** - Last modification date (dataset maintenance)
- **`TrendingScoreMetric`** - Trending score (popularity velocity)

**Optional Metrics** (require HELM leaderboard JSONL file):
- **`TopNModelsMetric`** - Top 5 performing models for each dataset (commented out, ready to enable)
- **`IsSaturatedMetric`** - Whether the benchmark is saturated (commented out, ready to enable)

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

1. **Data source**: Uses `data/all_datasets.json` (shared with hf_openllm_v2) instead of separate HELM metadata file
2. **Error handling**: All dataset classes include try-except blocks for loading datasets, with fallback to metadata values
3. **Configuration handling**: NaturalQuestions has both closed-book and open-book configurations
4. **CSV export**: Generates `metrics_output_helm_classic.csv` with all metrics (same format as hf_openllm_v2)
5. **Leaderboard JSONL**: To enable `top_5_models` and `is_saturated` metrics, provide `data/leaderboard_data/helm_data.jsonl` and uncomment lines 211-228 in `run_metrics.py`



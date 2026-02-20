# HELM Dynamic Metrics Implementation

## Overview

Dynamic metrics track time-varying properties of HELM datasets. Unlike static metrics (which never change), dynamic metrics are updated periodically to capture how dataset popularity, freshness, and community engagement evolve over time.

## Implemented Dynamic Metrics

### 1. Dataset Downloads Metric
**File**: `analyzer/src/metrics/dynamic/dataset_downloads_metric.py`  
**Description**: Tracks the number of times a dataset has been downloaded from Hugging Face  
**Update Frequency**: 7 days (configurable)  
**Data Source**: `downloads` field from dataset metadata  
**Purpose**: Indicates dataset popularity and real-world usage

### 2. Dataset Likes Metric
**File**: `analyzer/src/metrics/dynamic/dataset_likes_metric.py`  
**Description**: Tracks the number of likes/stars a dataset has received on Hugging Face  
**Update Frequency**: 7 days (configurable)  
**Data Source**: `likes` field from dataset metadata  
**Purpose**: Measures community appreciation and interest

### 3. Dataset Freshness Metric
**File**: `analyzer/src/metrics/dynamic/dataset_freshness_metric.py`  
**Description**: Tracks when the dataset was last modified/updated  
**Update Frequency**: 7 days (configurable)  
**Data Source**: `last_modified` field from dataset metadata  
**Purpose**: Indicates how actively maintained the dataset is

### 4. Trending Score Metric
**File**: `analyzer/src/metrics/dynamic/trending_score_metric.py`  
**Description**: Tracks the dataset's trending score (popularity velocity)  
**Update Frequency**: 7 days (configurable)  
**Data Source**: `trending_score` field from dataset metadata  
**Purpose**: Identifies datasets gaining rapid attention

## Architecture

### Base Class: UpdatableMetric

All dynamic metrics inherit from `UpdatableMetric` (defined in `analyzer/src/metrics/dynamic/base.py`):

```python
class UpdatableMetric(Metric):
    - Stores historical values with timestamps
    - Implements update frequency checks
    - Provides methods to track changes over time
```

### Key Methods

- **`_compute_current(dataset)`** - Fetches current value from dataset metadata
- **`run(dataset)`** - Computes current value and stores it with timestamp
- **`get_historical_values(dataset)`** - Returns all historical measurements
- **`needs_update(dataset)`** - Checks if enough time has passed for an update

## Integration with HELM Datasets

### Dataset Classes
Each HELM dataset class (banking77.py, financebench.py, etc.) includes dynamic metric fields in its `process()` method:

```python
def process(self, data: Dict[str, Any]):
    # ... static fields ...
    
    # Extract dynamic metric fields
    downloads = data.get("downloads", 0)
    likes = data.get("likes", 0)
    last_modified = data.get("last_modified", "")
    trending_score = data.get("trending_score", 0.0)
    
    final_df = pd.DataFrame({
        # ... other fields ...
        "downloads": [downloads],
        "likes": [likes],
        "last_modified": [last_modified],
        "trending_score": [trending_score],
    })
```

### Metrics Runner

`run_metrics.py` runs both static and dynamic metrics:

```python
# Define dynamic metrics to run
dynamic_metrics = [
    DatasetDownloadsMetric(name="dataset_downloads"),
    DatasetLikesMetric(name="dataset_likes"),
    DatasetFreshnessMetric(name="dataset_freshness"),
    TrendingScoreMetric(name="trending_score"),
]

# Run all dynamic metrics
for metric in dynamic_metrics:
    metric_result = metric.run_on_leaderboard(helm_leaderboard)
    all_metric_results[metric_name] = metric_result
```

## Data Flow

1. **Metadata Collection** → `data/extract_helm_dataset_metadata.py` pulls dataset info from YAML exports
2. **JSON Storage** → Metadata saved to `data/helm_dataset_metadata.json`
3. **Dataset Processing** → Each dataset class loads and processes metadata
4. **Metric Computation** → Dynamic metrics extract time-varying fields
5. **Historical Tracking** → Values stored with timestamps for trend analysis

## Usage Example

```python
from analyzer.src.leaderboards.helm.banking77 import Banking77Dataset
from analyzer.src.metrics.dynamic.dataset_downloads_metric import DatasetDownloadsMetric

# Initialize dataset
dataset = Banking77Dataset(
    name="banking77",
    paper_url="...",
    dataset_url="...",
    hf_dataset_id="mteb/banking77",
    static_data_path="data/helm_dataset_metadata.json"
)

# Load and process data
metadata = dataset.download()
dataset.process(metadata["datasets"]["mteb/banking77"])

# Run dynamic metric
downloads_metric = DatasetDownloadsMetric()
current_downloads = downloads_metric.run(dataset)

# Get historical values
history = downloads_metric.get_historical_values(dataset)
print(f"Download history: {history}")
```

## Running All Metrics

To run both static and dynamic metrics on all HELM datasets:

```bash
cd /Users/srishtiy/dev/benchmark-saturation
python3 -m analyzer.src.leaderboards.helm.run_metrics
```

Output includes:
- ✓ Status for each metric
- Current values for all datasets
- Error messages if any metric fails
- Dataset rankings table

## Benefits of Dynamic Metrics

1. **Trend Analysis** - Track how dataset popularity changes over time
2. **Early Detection** - Identify emerging/declining datasets via trending scores
3. **Maintenance Monitoring** - Alert when datasets become stale (no recent updates)
4. **Community Insights** - Understand which datasets the community values most
5. **Historical Context** - Compare current metrics to past values

## Future Enhancements

Potential additions:
- Citation count tracking (from academic papers)
- Issue/PR activity on GitHub repos
- Model performance trends on each dataset
- Dataset quality metrics over time
- Community contribution rates

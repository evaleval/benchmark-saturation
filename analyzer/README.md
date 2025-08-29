# Benchmark Analyzer

The scripts for Team 3's (infrastructure) work.

A series of metrics, implemented in python, which transform an input csv of benchmark information (chiefly links to hf repos and downloads, other metadata) into additional csv rows in place.

"Metric" here is an abstraction that represents any *number* generated from a dataset or leaderboard. This can include live checks of citation counts, etc.

For now, we are implementing these metrics to be individually run manually, but we will eventually transition to an automated pipeline.

## Adding a New Dataset

To add a new dataset to the system, follow these steps:

### 1. Create a Dataset Folder

Create a new folder under `src/benchmarks/` with your dataset name:

```bash
mkdir -p src/benchmarks/your_dataset_name
```

### 2. Implement Your Dataset Class

Create a new Python file in your dataset folder that implements the `Dataset` base class:

```python
# src/benchmarks/your_dataset_name/dataset.py
from typing import Any, Optional
import pandas as pd
from analyzer.src.metrics.base import Dataset

class YourDatasetName(Dataset):
    """
    Description of your dataset.
    """
    
    def __init__(self, name: str, paper_url: Optional[str] = None, dataset_url: Optional[str] = None, description: str = ""):
        super().__init__(name, paper_url, dataset_url, description)
        # Add any dataset-specific initialization
    
    def refresh(self) -> None:
        """
        Pull down new information from any updatable sources.
        Implement your data refresh logic here.
        """
        # Download fresh data
        raw_data = self.download()
        # Process and store it
        self.data = self.process(raw_data)
    
    def download(self) -> Any:
        """
        Download the dataset.
        Implement your data download logic here.
        """
        # Implement actual download logic
        return {}
    
    def process(self, data: Any) -> pd.DataFrame:
        """
        Process downloaded data into a pandas DataFrame.
        """
        # Implement data processing logic
        return pd.DataFrame()
    
    def get_citations(self) -> int:
        """
        Get the current citation count for the dataset's associated paper.
        Implement citation fetching logic if applicable.
        """
        return 0
```

### 3. Create a Leaderboard Class (Optional)

If you want to group multiple datasets under a leaderboard, create a leaderboard class:

```python
# src/benchmarks/your_leaderboard_name/leaderboard.py
import pandas as pd
from analyzer.src.metrics.base import Leaderboard, Dataset

class YourLeaderboardName(Leaderboard):
    """
    Description of your leaderboard that contains multiple datasets.
    """
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        # Add any leaderboard-specific initialization
    
    def refresh(self) -> None:
        """
        Refresh the leaderboard's own data (e.g., rankings, metadata).
        This is separate from refreshing individual datasets.
        """
        # Implement leaderboard-specific refresh logic
        # For example, fetch updated rankings from an external API
        pass
    
    def compute_rankings(self) -> pd.DataFrame:
        """
        Compute rankings across all datasets.
        """
        # Implement ranking computation logic
        rankings_data = []
        for dataset_name, dataset in self.datasets.items():
            # Example ranking computation
            rankings_data.append({
                'dataset': dataset_name,
                'citations': dataset.get_citations(),
                # Add other ranking criteria
            })
        
        return pd.DataFrame(rankings_data)
```

### 4. Create Dataset-Specific Metrics

In your dataset folder, create metric files for both static and dynamic metrics:

#### Static Metrics
Create `src/benchmarks/your_dataset_name/static_metrics.py`:

```python
from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict

class YourStaticMetric(StaticMetric):
    """
    A static metric that doesn't change over time.
    """
    
    def __init__(self):
        super().__init__(
            name="your_static_metric",
            description="Description of what this metric measures"
        )
    
    def calculate(self, target: Union[Dataset, Leaderboard]) -> Union[float, Dict[str, float]]:
        """
        Calculate the static metric value.
        """
        if isinstance(target, Dataset):
            # Calculate metric for a single dataset
            return 0.0
        elif isinstance(target, Leaderboard):
            # Calculate metric for each dataset in the leaderboard
            results = {}
            for dataset_name, dataset in target.datasets.items():
                results[dataset_name] = self.calculate(dataset)
            return results
```

#### Dynamic Metrics
Create `src/benchmarks/your_dataset_name/dynamic_metrics.py`:

```python
from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict

class YourDynamicMetric(UpdatableMetric):
    """
    A dynamic metric that may change over time.
    """
    
    def __init__(self):
        super().__init__(
            name="your_dynamic_metric",
            description="Description of what this metric measures"
        )
    
    def calculate(self, target: Union[Dataset, Leaderboard]) -> Union[float, Dict[str, float]]:
        """
        Calculate the dynamic metric value.
        """
        if isinstance(target, Dataset):
            # Calculate metric for a single dataset
            return 0.0
        elif isinstance(target, Leaderboard):
            # Calculate metric for each dataset in the leaderboard
            results = {}
            for dataset_name, dataset in target.datasets.items():
                results[dataset_name] = self.calculate(dataset)
            return results
    
    def update(self) -> None:
        """
        Update any cached data for this metric.
        """
        pass
```

### 5. Create Package Files

Add an `__init__.py` file to make your dataset folder a Python package:

```python
# src/benchmarks/your_dataset_name/__init__.py
from analyzer.src.benchmarks.your_dataset_name.dataset import YourDatasetName
from analyzer.src.benchmarks.your_dataset_name.static_metrics import YourStaticMetric
from analyzer.src.benchmarks.your_dataset_name.dynamic_metrics import YourDynamicMetric

__all__ = [
    'YourDatasetName',
    'YourStaticMetric', 
    'YourDynamicMetric'
]
```

If you created a leaderboard, also add:

```python
# src/benchmarks/your_leaderboard_name/__init__.py
from analyzer.src.benchmarks.your_leaderboard_name.leaderboard import YourLeaderboardName

__all__ = ['YourLeaderboardName']
```

### 6. Register Your Dataset/Leaderboard

Add your dataset/leaderboard to the main benchmarks `__init__.py` file if needed, or import it in your usage scripts.

### 7. Example Usage

Here's how to use your new dataset and leaderboard:

```python
from analyzer.src.benchmarks.your_dataset_name import YourDatasetName, YourStaticMetric, YourDynamicMetric
from analyzer.src.benchmarks.your_leaderboard_name import YourLeaderboardName

# Create dataset instances
dataset1 = YourDatasetName(
    name="Dataset 1",
    paper_url="https://example.com/paper1",
    dataset_url="https://example.com/dataset1"
)

dataset2 = YourDatasetName(
    name="Dataset 2", 
    paper_url="https://example.com/paper2",
    dataset_url="https://example.com/dataset2"
)

# Create leaderboard and add datasets
leaderboard = YourLeaderboardName(
    name="My Benchmark Leaderboard",
    description="A leaderboard containing multiple datasets"
)
leaderboard.add_dataset(dataset1)
leaderboard.add_dataset(dataset2)

# Create and run metrics on individual datasets
static_metric = YourStaticMetric()
dynamic_metric = YourDynamicMetric()

# Run metrics on a single dataset
dataset_static_score = static_metric.run_on_dataset(dataset1)
dataset_dynamic_score = dynamic_metric.run_on_dataset(dataset1)

# Run metrics on entire leaderboard (returns scores for all datasets)
leaderboard_static_scores = static_metric.run_on_leaderboard(leaderboard)
leaderboard_dynamic_scores = dynamic_metric.run_on_leaderboard(leaderboard)

# Refresh data
dataset1.refresh()  # Refresh individual dataset
leaderboard.refresh_all()  # Refresh all datasets in leaderboard
leaderboard.refresh()  # Refresh leaderboard metadata only

# Get rankings
rankings = leaderboard.compute_rankings()
print(rankings)
```

## Metric Types

- **Static Metrics** (`src/metrics/static/`): Numbers that never change for a dataset, such as dataset size or complexity measures. These are calculated once when the dataset is added.

- **Dynamic Metrics** (`src/metrics/dynamic/`): Time-specific information that may change, such as download counts, citations, or leaderboard scores. These can be updated periodically.

## Architecture

The system is built around three main abstract base classes:

- **`Dataset`**: Represents an individual dataset or evaluation task with metadata and data access methods. Contains methods for downloading, processing, and refreshing data.

- **`Leaderboard`**: Represents a collection of datasets that can be managed and analyzed together. Provides methods for adding/removing datasets, computing rankings, and aggregating metrics.

- **`Metric`**: Represents any numerical measurement that can be calculated from a dataset or leaderboard. Metrics can work on individual datasets or across entire leaderboards.

### Class Hierarchy
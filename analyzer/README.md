# Benchmark Analyzer

The scripts for Team 3's (infrastructure) work.

A series of metrics, implemented in python, which transform an input csv of benchmark information (chiefly links to hf repos and downloads, other metadata) into additional csv rows in place.

"Metric" here is an abstraction that represents any *number* generated from a dataset. This can include live checks of citation counts, etc.

For now, we are implementing these metrics to be individually run manually, but we will eventually transition to an automated pipeline.

## Adding a New Benchmark

To add a new benchmark to the system, follow these steps:

### 1. Create a Benchmark Folder

Create a new folder under `src/benchmarks/` with your benchmark name:

```bash
mkdir -p src/benchmarks/your_benchmark_name
```

### 2. Implement Your Benchmark Class

Create a new Python file in your benchmark folder that implements the `Benchmark` base class:

```python
# src/benchmarks/your_benchmark_name/benchmark.py
from typing import Any, Optional
import pandas as pd
from analyzer.src.metrics.base import Benchmark

class YourBenchmarkName(Benchmark):
    """
    Description of your benchmark.
    """
    
    def __init__(self, paper_url: Optional[str] = None, dataset_url: Optional[str] = None):
        super().__init__(paper_url, dataset_url)
        # Add any benchmark-specific initialization
    
    def refresh(self) -> None:
        """
        Pull down new information from any updatable sources.
        Implement your data refresh logic here.
        """
        pass
    
    def get_citations(self) -> int:
        """
        Get the current citation count for the benchmark's associated paper.
        Implement citation fetching logic if applicable.
        """
        return 0
    
    def download(self) -> Any:
        """
        Download the benchmark dataset.
        Implement your data download logic here.
        """
        return None
    
    def process(self, data: Any) -> pd.DataFrame:
        """
        Process downloaded data into a pandas DataFrame.
        """
        return pd.DataFrame()
```

### 3. Create Benchmark-Specific Metrics

In your benchmark folder, create metric files for both static and dynamic metrics:

#### Static Metrics
Create `src/benchmarks/your_benchmark_name/static_metrics.py`:

```python
from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.base import Benchmark

class YourStaticMetric(StaticMetric):
    """
    A static metric that doesn't change over time.
    """
    
    def __init__(self):
        super().__init__(
            name="your_static_metric",
            description="Description of what this metric measures"
        )
    
    def calculate(self, benchmark: Benchmark) -> float:
        """
        Calculate the static metric value.
        """
        # Implement your static metric calculation
        return 0.0
```

#### Dynamic Metrics
Create `src/benchmarks/your_benchmark_name/dynamic_metrics.py`:

```python
from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Benchmark

class YourDynamicMetric(UpdatableMetric):
    """
    A dynamic metric that may change over time.
    """
    
    def __init__(self):
        super().__init__(
            name="your_dynamic_metric",
            description="Description of what this metric measures"
        )
    
    def calculate(self, benchmark: Benchmark) -> float:
        """
        Calculate the dynamic metric value.
        """
        # Implement your dynamic metric calculation
        return 0.0
    
    def update(self) -> None:
        """
        Update any cached data for this metric.
        """
        pass
```

### 4. Create Package Files

Add an `__init__.py` file to make your benchmark folder a Python package:

```python
# src/benchmarks/your_benchmark_name/__init__.py
from analyzer.src.benchmarks.your_benchmark_name.benchmark import YourBenchmarkName
from analyzer.src.benchmarks.your_benchmark_name.static_metrics import YourStaticMetric
from analyzer.src.benchmarks.your_benchmark_name.dynamic_metrics import YourDynamicMetric

__all__ = [
    'YourBenchmarkName',
    'YourStaticMetric', 
    'YourDynamicMetric'
]
```

### 5. Register Your Benchmark

Add your benchmark to the main benchmarks `__init__.py` file if needed, or import it in your usage scripts.

### 6. Example Usage

Here's how to use your new benchmark:

```python
from analyzer.src.benchmarks.your_benchmark_name import YourBenchmarkName, YourStaticMetric, YourDynamicMetric

# Create benchmark instance
benchmark = YourBenchmarkName(
    paper_url="https://example.com/paper",
    dataset_url="https://example.com/dataset"
)

# Create and run metrics
static_metric = YourStaticMetric()
dynamic_metric = YourDynamicMetric()

static_score = static_metric.run(benchmark)
dynamic_score = dynamic_metric.run(benchmark)
```

## Metric Types

- **Static Metrics** (`src/metrics/static/`): Numbers that never change for a benchmark, such as dataset size or complexity measures. These are calculated once when the benchmark is added.

- **Dynamic Metrics** (`src/metrics/dynamic/`): Time-specific information that may change, such as download counts, citations, or leaderboard scores. These can be updated periodically.

## Architecture

The system is built around two main abstract base classes:

- `Benchmark`: Represents a dataset or evaluation task with metadata and data access methods
- `Metric`: Represents any numerical measurement that can be calculated from a benchmark

Benchmarks are organized in `src/benchmarks/` while the metric framework lives in `src/metrics/`. See `src/metrics/examples.py` for complete working examples of benchmark and metric implementations.
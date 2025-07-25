For context, whenever we use cursor or other AI code assistants to generate code for this project, I will be placing some of the included text they produce to explain the outputs here

# Base Classes Created:

## 1. Benchmark (Abstract Base Class)
- Represents datasets or evaluation tasks that can be analyzed
- Contains metadata like `paper_url` and `dataset_url`
- Has abstract `refresh()` method for updating from external sources
- Provides methods for citation counting, data downloading, and processing
- Includes a data property for storing processed pandas DataFrames

## 2. Metric (Abstract Base Class)
- Base class for all metrics
- Has name and description attributes
- Abstract run(benchmark) method that returns a float score
- Includes helpful string representations

## 3. StaticMetric (Inherits from Metric)
- For metrics that are computed once and don't change
- Caches computed values to avoid recomputation
- Abstract _compute(benchmark) method for the actual computation
- Includes benchmark identification for caching

## 4. UpdatableMetric (Inherits from Metric)
- For metrics that change over time and need periodic updates
- Tracks historical values with timestamps
- Configurable update frequency (default 7 days)
- Abstract _compute_current(benchmark) method
- Includes needs_update() method to check if refresh is needed
- Provides get_historical_values() for accessing historical data

## Key Features:
- Minimal but extensible: The classes provide sensible defaults while allowing customization
- Type hints: Full typing support for better IDE integration and code clarity
- Caching: Static metrics cache their results, updatable metrics track history
- Flexible identification: Benchmark identification can be customized per metric type
- Clear separation: Static vs dynamic metrics are clearly separated in the folder structure

# Usage example

```python
from analyzer.src.metrics import Benchmark, StaticMetric, UpdatableMetric

# Create a static metric
class NumClassesMetric(StaticMetric):
    def _compute(self, benchmark):
        return len(benchmark.data.columns) if benchmark.data is not None else 0

# Create an updatable metric  
class CitationCountMetric(UpdatableMetric):
    def _compute_current(self, benchmark):
        return benchmark.get_citations()
```
"""
Example implementations and usage of the metrics architecture.

This file demonstrates how to create concrete benchmarks and metrics,
and how to use them together.
"""

import pandas as pd
from typing import Any, Optional
from analyzer.src.metrics.base import Benchmark 
from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.dynamic.base import UpdatableMetric


# ============================================================================
# Example Benchmark Implementation
# ============================================================================

class ExampleBenchmark(Benchmark):
    """
    A concrete implementation of a benchmark.
    
    This example benchmark represents a dataset with some basic metadata
    and the ability to download and process data.
    """
    
    def __init__(self, name: str, paper_url: Optional[str] = None, 
                 dataset_url: Optional[str] = None, initial_data: Optional[pd.DataFrame] = None):
        super().__init__(paper_url, dataset_url)
        self.name = name
        if initial_data is not None:
            self._data = initial_data
    
    def refresh(self) -> None:
        """
        Refresh the benchmark data from external sources.
        In a real implementation, this might fetch new data from APIs.
        """
        print(f"Refreshing benchmark: {self.name}")
        # Simulate fetching new data
        if self.dataset_url:
            print(f"Downloading from: {self.dataset_url}")
    
    def get_citations(self) -> int:
        """
        Get citation count for the benchmark's paper.
        In a real implementation, this would call an API.
        """
        # Simulate API call
        import random
        return random.randint(10, 1000)
    
    def download(self) -> Any:
        """
        Download the benchmark dataset.
        """
        # Simulate downloading data
        return {"data": "simulated_downloaded_data"}
    
    def process(self, data: Any) -> pd.DataFrame:
        """
        Process downloaded data into a pandas DataFrame.
        """
        # Simulate processing data
        return pd.DataFrame({
            'text': ['sample text 1', 'sample text 2', 'sample text 3'],
            'label': [0, 1, 0],
            'length': [12, 13, 12]
        })


# ============================================================================
# Example Static Metrics
# ============================================================================

class NumSamplesMetric(StaticMetric):
    """
    A static metric that counts the number of samples in a benchmark.
    """
    
    def __init__(self):
        super().__init__("num_samples", "Number of samples in the benchmark")
    
    def _compute(self, benchmark: Benchmark) -> float:
        if benchmark.data is None:
            return 0.0
        return float(len(benchmark.data))


class AvgTextLengthMetric(StaticMetric):
    """
    A static metric that calculates the average text length.
    """
    
    def __init__(self):
        super().__init__("avg_text_length", "Average length of text samples")
    
    def _compute(self, benchmark: Benchmark) -> float:
        if benchmark.data is None or 'length' not in benchmark.data.columns:
            return 0.0
        
        return benchmark.data['length'].mean()


class NumClassesMetric(StaticMetric):
    """
    A static metric that counts the number of unique classes.
    """
    
    def __init__(self):
        super().__init__("num_classes", "Number of unique classes in the benchmark")
    
    def _compute(self, benchmark: Benchmark) -> float:
        if benchmark.data is None or 'label' not in benchmark.data.columns:
            return 0.0
        
        return float(benchmark.data['label'].nunique())


# ============================================================================
# Example Dynamic Metrics
# ============================================================================

class CitationCountMetric(UpdatableMetric):
    """
    A dynamic metric that tracks citation count over time.
    """
    
    def __init__(self):
        super().__init__("citation_count", "Number of citations for the benchmark's paper", update_frequency_days=30)
    
    def _compute_current(self, benchmark: Benchmark) -> float:
        return float(benchmark.get_citations())


class DownloadCountMetric(UpdatableMetric):
    """
    A dynamic metric that tracks download count (simulated).
    """
    
    def __init__(self):
        super().__init__("download_count", "Number of downloads for the benchmark", update_frequency_days=7)
    
    def _compute_current(self, benchmark: Benchmark) -> float:
        # Simulate download count based on benchmark name
        import random
        import hashlib
        # Use benchmark name to generate consistent "random" numbers
        seed = int(hashlib.md5(benchmark.name.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        return float(random.randint(100, 10000))


# ============================================================================
# Example Usage
# ============================================================================

def run_example():
    """
    Demonstrate how to use the metrics architecture.
    """
    print("=== Metrics Architecture Example ===\n")
    
    # Create a benchmark with some sample data
    sample_data = pd.DataFrame({
        'text': ['This is a sample text', 'Another sample text', 'Yet another sample'],
        'label': [0, 1, 0],
        'length': [19, 18, 20]
    })
    
    benchmark = ExampleBenchmark(
        name="example_benchmark",
        paper_url="https://example.com/paper",
        dataset_url="https://example.com/dataset",
        initial_data=sample_data
    )
    
    print(f"Created benchmark: {benchmark.name}")
    print(f"Data shape: {benchmark.data.shape}")
    print()
    
    # Create static metrics
    static_metrics = [
        NumSamplesMetric(),
        AvgTextLengthMetric(),
        NumClassesMetric()
    ]
    
    print("=== Running Static Metrics ===")
    for metric in static_metrics:
        score = metric.run(benchmark)
        print(f"{metric.name}: {score}")
    
    print()
    
    # Create dynamic metrics
    dynamic_metrics = [
        CitationCountMetric(),
        DownloadCountMetric()
    ]
    
    print("=== Running Dynamic Metrics ===")
    for metric in dynamic_metrics:
        score = metric.run(benchmark)
        print(f"{metric.name}: {score}")
        
        # Show historical values
        historical = metric.get_historical_values(benchmark)
        if historical:
            print(f"  Historical values: {len(historical)} entries")
    
    print()
    
    # Demonstrate caching for static metrics
    print("=== Demonstrating Static Metric Caching ===")
    num_samples_metric = NumSamplesMetric()
    score1 = num_samples_metric.run(benchmark)
    score2 = num_samples_metric.run(benchmark)
    print(f"First run: {score1}")
    print(f"Second run: {score2}")
    print(f"Values are cached: {score1 == score2}")
    
    print()
    
    # Demonstrate update frequency for dynamic metrics
    print("=== Demonstrating Dynamic Metric Update Frequency ===")
    citation_metric = CitationCountMetric()
    print(f"Needs update: {citation_metric.needs_update(benchmark)}")
    
    # Run the metric
    score = citation_metric.run(benchmark)
    print(f"Citation count: {score}")
    
    # Check if it needs update again (should be False since we just ran it)
    print(f"Needs update after running: {citation_metric.needs_update(benchmark)}")


if __name__ == "__main__":
    run_example() 
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd

__all__ = ['Benchmark', 'Metric', 'StaticMetric', 'UpdatableMetric']


class Benchmark(ABC):
    """
    Abstract base class for benchmarks.
    
    Benchmarks represent datasets or evaluation tasks that can be analyzed
    by various metrics. They contain metadata and can refresh their data
    from external sources.
    """
    
    def __init__(self, paper_url: Optional[str] = None, dataset_url: Optional[str] = None):
        self.paper_url = paper_url
        self.dataset_url = dataset_url
        self._data: Optional[pd.DataFrame] = None
    
    @abstractmethod
    def refresh(self) -> None:
        """
        Pull down new information from any updatable sources.
        This method should update the benchmark's internal state.
        """
        pass
    
    def get_citations(self) -> int:
        """
        Get the current citation count for the benchmark's associated paper.
        
        Returns:
            int: Number of citations
        """
        # Default implementation - subclasses should override
        return 0
    
    def download(self) -> Any:
        """
        Download the benchmark dataset.
        
        Returns:
            Any: The downloaded dataset
        """
        # Default implementation - subclasses should override
        return None
    
    def process(self, data: Any) -> pd.DataFrame:
        """
        Process downloaded data into a pandas DataFrame.
        
        Args:
            data: The downloaded data
            
        Returns:
            pd.DataFrame: Processed data
        """
        # Default implementation - subclasses should override
        return pd.DataFrame()
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get the processed benchmark data."""
        return self._data
    
    @data.setter
    def data(self, value: pd.DataFrame):
        """Set the processed benchmark data."""
        self._data = value


class Metric(ABC):
    """
    Abstract base class for all metrics.
    
    Metrics analyze benchmarks and produce numerical scores or other
    quantitative measurements.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, benchmark: Benchmark) -> float:
        """
        Run the metric on a benchmark and return a score.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The metric score
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"


class StaticMetric(Metric):
    """
    Abstract base class for static metrics.
    
    Static metrics are computed once when a benchmark is added and
    their values don't change over time.
    """
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self._computed_values: Dict[str, float] = {}
    
    def run(self, benchmark: Benchmark) -> float:
        """
        Run the static metric on a benchmark.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The static metric score
        """
        # Check if we've already computed this value
        benchmark_id = self._get_benchmark_id(benchmark)
        if benchmark_id in self._computed_values:
            return self._computed_values[benchmark_id]
        
        # Compute the value
        score = self._compute(benchmark)
        self._computed_values[benchmark_id] = score
        return score
    
    @abstractmethod
    def _compute(self, benchmark: Benchmark) -> float:
        """
        Compute the static metric value.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The computed metric score
        """
        pass
    
    def _get_benchmark_id(self, benchmark: Benchmark) -> str:
        """
        Get a unique identifier for the benchmark.
        
        Args:
            benchmark: The benchmark
            
        Returns:
            str: Unique identifier
        """
        # Default implementation - subclasses can override
        return f"{benchmark.__class__.__name__}_{id(benchmark)}"


class UpdatableMetric(Metric):
    """
    Abstract base class for updatable metrics.
    
    Updatable metrics are computed periodically and track historical values
    over time. They may depend on external data sources that change.
    """
    
    def __init__(self, name: str, description: str = "", update_frequency_days: int = 7):
        super().__init__(name, description)
        self.update_frequency_days = update_frequency_days
        self._historical_values: Dict[str, Dict[str, float]] = {}  # benchmark_id -> {timestamp: value}
    
    def run(self, benchmark: Benchmark) -> float:
        """
        Run the updatable metric on a benchmark.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The current metric score
        """
        benchmark_id = self._get_benchmark_id(benchmark)
        current_value = self._compute_current(benchmark)
        
        # Store the historical value
        if benchmark_id not in self._historical_values:
            self._historical_values[benchmark_id] = {}
        
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        self._historical_values[benchmark_id][timestamp] = current_value
        
        return current_value
    
    @abstractmethod
    def _compute_current(self, benchmark: Benchmark) -> float:
        """
        Compute the current value of the updatable metric.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The current metric score
        """
        pass
    
    def get_historical_values(self, benchmark: Benchmark) -> Dict[str, float]:
        """
        Get historical values for a benchmark.
        
        Args:
            benchmark: The benchmark
            
        Returns:
            Dict[str, float]: Historical values with timestamps as keys
        """
        benchmark_id = self._get_benchmark_id(benchmark)
        return self._historical_values.get(benchmark_id, {})
    
    def _get_benchmark_id(self, benchmark: Benchmark) -> str:
        """
        Get a unique identifier for the benchmark.
        
        Args:
            benchmark: The benchmark
            
        Returns:
            str: Unique identifier
        """
        # Default implementation - subclasses can override
        return f"{benchmark.__class__.__name__}_{id(benchmark)}"
    
    def needs_update(self, benchmark: Benchmark) -> bool:
        """
        Check if the metric needs to be updated for this benchmark.
        
        Args:
            benchmark: The benchmark
            
        Returns:
            bool: True if update is needed
        """
        # Simple implementation - can be overridden for more sophisticated logic
        import datetime
        benchmark_id = self._get_benchmark_id(benchmark)
        
        if benchmark_id not in self._historical_values:
            return True
        
        if not self._historical_values[benchmark_id]:
            return True
        
        # Check if the last update was more than update_frequency_days ago
        last_timestamp = max(self._historical_values[benchmark_id].keys())
        last_update = datetime.datetime.fromisoformat(last_timestamp)
        days_since_update = (datetime.datetime.now() - last_update).days
        
        return days_since_update >= self.update_frequency_days

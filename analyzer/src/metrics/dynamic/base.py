from typing import Dict
from ..base import Metric, Benchmark


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
    
    def _compute_current(self, benchmark: Benchmark) -> float:
        """
        Compute the current value of the updatable metric.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The current metric score
        """
        raise NotImplementedError("Subclasses must implement _compute_current")
    
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

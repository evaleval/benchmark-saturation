from typing import Dict
from analyzer.src.metrics.base import Metric, Benchmark


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
    
    def _compute(self, benchmark: Benchmark) -> float:
        """
        Compute the static metric value.
        
        Args:
            benchmark: The benchmark to analyze
            
        Returns:
            float: The computed metric score
        """
        raise NotImplementedError("Subclasses must implement _compute")
    
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

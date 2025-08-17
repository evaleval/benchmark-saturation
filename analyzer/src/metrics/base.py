from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class Benchmark(ABC):
    """
    Abstract base class for benchmarks.
    
    Benchmarks represent datasets or evaluation tasks that can be analyzed
    by various metrics. They contain metadata and can refresh their data
    from external sources.
    """
    
    def __init__(self, dataset_name: str, paper_url: Optional[str] = None, dataset_url: Optional[str] = None, ds_id: Optional[str] = None):
        self.dataset_name = dataset_name
        self.paper_url = paper_url
        self.dataset_url = dataset_url
        self.ds_id = ds_id
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

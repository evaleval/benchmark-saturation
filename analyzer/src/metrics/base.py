from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import pandas as pd


class Dataset(ABC):
    """
    Abstract base class for individual datasets/benchmarks.

    Datasets represent individual evaluation tasks that can be analyzed
    by various metrics. They contain metadata and can refresh their data
    from external sources.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        paper_url: Optional[str] = None,
        dataset_url: Optional[str] = None,
        hf_dataset_id: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.paper_url = paper_url
        self.dataset_url = dataset_url
        self.hf_dataset_id = hf_dataset_id
        self._data: Optional[pd.DataFrame] = None

    @abstractmethod
    def refresh(self) -> None:
        """
        Pull down new information from any updatable sources.
        This method should update the dataset's internal state.
        """
        pass

    @abstractmethod
    def download(self) -> Any:
        """
        Download the dataset.

        Returns:
            Any: The downloaded dataset
        """
        pass

    @abstractmethod
    def process(self, data: Any) -> pd.DataFrame:
        """
        Process downloaded data into a pandas DataFrame.

        Args:
            data: The downloaded data

        Returns:
            pd.DataFrame: Processed data
        """
        pass

    def get_citations(self) -> int:
        """
        Get the current citation count for the dataset's associated paper.

        Returns:
            int: Number of citations
        """
        # Default implementation - subclasses should override
        return 0

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get the processed dataset data."""
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame):
        """Set the processed dataset data."""
        self._data = value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"


class Leaderboard(ABC):
    """
    Abstract base class for leaderboards that contain multiple datasets.

    Leaderboards aggregate multiple datasets and provide methods to manage
    and analyze them collectively.
    """

    def __init__(self, name: str, description: str = "", **kwargs):
        self.name = name
        self.description = description
        self._datasets: Dict[str, Dataset] = {}

    def add_dataset(self, dataset: Dataset) -> None:
        """
        Add a dataset to the leaderboard.

        Args:
            dataset: The dataset to add
        """
        self._datasets[dataset.name] = dataset

    def remove_dataset(self, dataset_name: str) -> None:
        """
        Remove a dataset from the leaderboard.

        Args:
            dataset_name: Name of the dataset to remove
        """
        if dataset_name in self._datasets:
            del self._datasets[dataset_name]

    def get_dataset(self, dataset_name: str) -> Optional[Dataset]:
        """
        Get a specific dataset by name.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dataset: The requested dataset, or None if not found
        """
        return self._datasets.get(dataset_name)

    @property
    def datasets(self) -> Dict[str, Dataset]:
        """Get all datasets in the leaderboard."""
        return self._datasets.copy()

    def refresh_all(self) -> None:
        """
        Refresh all datasets in the leaderboard.
        """
        for dataset in self._datasets.values():
            dataset.refresh()

    @abstractmethod
    def refresh(self) -> None:
        """
        Refresh the leaderboard's own data (e.g., rankings, metadata).
        This is separate from refreshing individual datasets.
        """
        pass

    @abstractmethod
    def compute_rankings(self) -> pd.DataFrame:
        """
        Compute rankings across all datasets.

        Returns:
            pd.DataFrame: Rankings data
        """
        pass

    def get_total_citations(self) -> int:
        """
        Get the total citation count across all datasets.

        Returns:
            int: Sum of citations from all datasets
        """
        return sum(dataset.get_citations() for dataset in self._datasets.values())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {len(self._datasets)} datasets)"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', datasets={list(self._datasets.keys())})"


class Metric(ABC):
    """
    Abstract base class for all metrics.

    Metrics analyze datasets and produce numerical scores or other
    quantitative measurements. They can work on individual datasets
    or across multiple datasets in a leaderboard.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def run(
        self, target: Union[Dataset, Leaderboard]
    ) -> Union[float, Dict[str, float]]:
        """
        Run the metric on a dataset or leaderboard.

        Args:
            target: The dataset or leaderboard to analyze

        Returns:
            Union[float, Dict[str, float]]: The metric score(s)
        """
        pass

    def run_on_dataset(self, dataset: Dataset) -> float:
        """
        Run the metric specifically on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: The metric score
        """
        result = self.run(dataset)
        if isinstance(result, dict):
            raise ValueError("run_on_dataset should return a single float")
        return result

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, float]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict[str, float]: Metric scores for each dataset
        """
        result = self.run(leaderboard)
        if isinstance(result, float):
            # If the metric returns a single score for the entire leaderboard
            return {leaderboard.name: result}
        return result

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"

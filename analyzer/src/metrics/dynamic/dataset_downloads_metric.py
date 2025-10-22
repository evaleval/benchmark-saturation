from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict


class DatasetDownloadsMetric(UpdatableMetric):
    """
    Tracks the number of downloads for a dataset over time.
    
    This metric pulls the download count from the dataset metadata
    and tracks how it changes over time.
    """

    def __init__(
        self, name: str = "dataset_downloads", description: str = "", update_frequency_days: int = 7
    ):
        super().__init__(name, description, update_frequency_days)

    def _compute_current(self, dataset: Dataset) -> float:
        """
        Get the current download count for the dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Current download count
        """
        data = dataset.data
        if data is None or data.empty:
            return 0.0
        
        # Try to get downloads from the dataset's metadata
        # This would typically be pulled from HuggingFace API or metadata JSON
        downloads = data.iloc[0].get("downloads", 0)
        return float(downloads) if downloads else 0.0

    def run_on_dataset(self, dataset: Dataset) -> float:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Current download count
        """
        return self.run(dataset)

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, float]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict[str, float]: Download counts for each dataset
        """
        datasets = leaderboard.datasets
        results = {}
        for dataset_name, dataset in datasets.items():
            results[dataset_name] = self.run(dataset)
        return results

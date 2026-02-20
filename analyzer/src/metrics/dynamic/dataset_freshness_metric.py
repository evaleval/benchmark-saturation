from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict
from datetime import datetime


class DatasetFreshnessMetric(UpdatableMetric):
    """
    Tracks when a dataset was last modified/updated.
    
    This metric monitors the last modification timestamp and can help
    identify datasets that are actively maintained vs. stale.
    """

    def __init__(
        self, name: str = "dataset_freshness", description: str = "", update_frequency_days: int = 7
    ):
        super().__init__(name, description, update_frequency_days)

    def _compute_current(self, dataset: Dataset) -> float:
        """
        Get the days since last modification for the dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Days since last modification (0 if modified today)
        """
        data = dataset.data
        if data is None or data.empty:
            return -1.0  # Unknown freshness
        
        # Try to get last_modified from the dataset's metadata
        last_modified = data.iloc[0].get("last_modified")
        
        if not last_modified:
            return -1.0  # Unknown freshness
        
        try:
            # Parse the last_modified timestamp (format: "2024-11-17T18:42:59Z")
            last_modified_dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
            current_dt = datetime.now(last_modified_dt.tzinfo)
            days_since_modified = (current_dt - last_modified_dt).days
            return float(days_since_modified)
        except (ValueError, AttributeError):
            return -1.0  # Error parsing date

    def run_on_dataset(self, dataset: Dataset) -> float:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Days since last modification
        """
        return self.run(dataset)

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, float]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict[str, float]: Days since last modification for each dataset
        """
        datasets = leaderboard.datasets
        results = {}
        for dataset_name, dataset in datasets.items():
            results[dataset_name] = self.run(dataset)
        return results

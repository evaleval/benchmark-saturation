from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict


class TrendingScoreMetric(UpdatableMetric):
    """
    Tracks the trending score for a dataset over time.
    
    This metric monitors how popular/trending a dataset is,
    which can indicate current community interest and adoption.
    """

    def __init__(
        self, name: str = "trending_score", description: str = "", update_frequency_days: int = 1
    ):
        # Trending scores change more frequently, so default to daily updates
        super().__init__(name, description, update_frequency_days)

    def _compute_current(self, dataset: Dataset) -> float:
        """
        Get the current trending score for the dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Current trending score
        """
        data = dataset.data
        if data is None or data.empty:
            return 0.0
        
        # Try to get trending_score from the dataset's metadata
        trending_score = data.iloc[0].get("trending_score", 0)
        return float(trending_score) if trending_score else 0.0

    def run_on_dataset(self, dataset: Dataset) -> float:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            float: Current trending score
        """
        return self.run(dataset)

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, float]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict[str, float]: Trending scores for each dataset
        """
        datasets = leaderboard.datasets
        results = {}
        for dataset_name, dataset in datasets.items():
            results[dataset_name] = self.run(dataset)
        return results

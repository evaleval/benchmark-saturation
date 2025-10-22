from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict


class TaskCategoryMetric(StaticMetric):
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)

    def _compute(self, dataset: Dataset) -> Union[float, str, list]:
        data = dataset.data
        if data is None:
            return "No data available"

        task_cat = data.iloc[0]["task_categories"]
        # Handle list of categories
        if isinstance(task_cat, list):
            return task_cat
        # Handle string or other types
        return task_cat

    def run_on_dataset(self, dataset: Dataset) -> Union[float, str, list]:
        return self._compute(dataset)

    def run_on_leaderboard(
        self, leaderboard: Leaderboard
    ) -> Dict[str, Union[float, str, list]]:
        datasets = leaderboard.datasets
        leaderboard_results = {}
        for dataset_name, dataset in datasets.items():
            dataset_result = self._compute(dataset)
            leaderboard_results[dataset_name] = dataset_result

        return leaderboard_results

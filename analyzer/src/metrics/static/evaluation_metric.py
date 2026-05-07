from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Union, Dict


class EvaluationMetric(StaticMetric):
    """
    EvaluationMetric (metric used for evaluation of the dataset benchmark, e.g. BLEU, F1 etc) for these datasets.
    """

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)

    def _compute(self, dataset: Dataset) -> Union[float, str]:
        data = dataset.data
        if data is None:
            return "No data available"

        return data.iloc[0]["eval_metrics"]

    def run_on_dataset(self, dataset: Dataset) -> Union[float, str]:
        return self._compute(dataset)

    def run_on_leaderboard(
        self, leaderboard: Leaderboard
    ) -> Dict[str, Union[float, str]]:
        datasets = leaderboard.datasets
        leaderboard_results = {}
        for dataset_name, dataset in datasets.items():
            dataset_result = self._compute(dataset)
            leaderboard_results[dataset_name] = dataset_result

        return leaderboard_results

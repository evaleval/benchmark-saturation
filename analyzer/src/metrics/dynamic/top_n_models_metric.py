from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Dict, Union, List
import json


class TopNModelsMetric(UpdatableMetric):
    """
    Metric to find top N performing models for each dataset from evaluation results.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        top_n: int = 10,
        jsonl_path: str = "",
        dataset_to_eval_map: Dict[str, str] = None,
    ):
        super().__init__(name, description)
        self.top_n = top_n
        self.jsonl_path = jsonl_path
        self._model_data = None

        # Map dataset names to evaluation names in JSONL
        self.dataset_to_eval_map = dataset_to_eval_map or {}

    def _load_model_data(self):
        """Load JSONL file once and cache it."""
        if self._model_data is None:
            self._model_data = []
            with open(self.jsonl_path, "r") as f:
                for line in f:
                    self._model_data.append(json.loads(line))
        return self._model_data

    def _compute(self, dataset: Dataset) -> List[Dict[str, Union[str, float]]]:
        """
        Compute top N models for a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            List of dicts containing model info and scores
        """
        model_data = self._load_model_data()
        eval_name = self.dataset_to_eval_map.get(dataset.name)

        if not eval_name:
            return []

        # Extract scores for this evaluation
        model_scores = []
        for model in model_data:
            for eval_result in model.get("evaluation_results", []):
                if eval_result["evaluation_name"] == eval_name:
                    model_scores.append(
                        {
                            "model_name": model["model_info"]["name"],
                            "developer": model["model_info"]["developer"],
                            "score": eval_result["score_details"]["score"],
                            "params_billions": model.get("additional_details", {}).get(
                                "params_billions"
                            ),
                            "architecture": model.get("additional_details", {}).get(
                                "architecture"
                            ),
                        }
                    )
                    break

        # Sort by score (descending) and get top N
        model_scores.sort(key=lambda x: x["score"], reverse=True)
        return model_scores[: self.top_n]

    def run_on_dataset(self, dataset: Dataset) -> List[Dict[str, Union[str, float]]]:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            List of top N models with their scores
        """
        return self._compute(dataset)

    def run_on_leaderboard(
        self, leaderboard: Leaderboard
    ) -> Dict[str, List[Dict[str, Union[str, float]]]]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict mapping dataset names to their top N models
        """
        datasets = leaderboard.datasets
        leaderboard_results = {}

        for dataset_name, dataset in datasets.items():
            dataset_result = self._compute(dataset)
            leaderboard_results[dataset_name] = dataset_result

        return leaderboard_results

    def _compute_current(self, leaderboard: Leaderboard) -> Dict[str, List[Dict]]:
        """
        Compute current top N models (for UpdatableMetric interface).
        """
        return self.run_on_leaderboard(leaderboard)

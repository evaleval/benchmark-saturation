from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Dict, Union, List
import json


class IsSaturatedMetric(UpdatableMetric):
    """
    Metric to determine if a benchmark is saturated.

    A benchmark is saturated if:
    1. Top N models score within X% of each other
    2. Mean performance of top N models > Z%
    3. Mean performance > (noise_ceiling - 2%)
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        top_n: int = 5,
        score_variance_threshold: float = 1.0,  # X = 1%
        min_mean_performance: float = 95.0,  # Z = 95%
        noise_ceiling: float = 97.0,  # B = 97%
        jsonl_path: str = "",
        dataset_to_eval_map: Dict[str, str] = None,
    ):
        super().__init__(name, description)
        self.top_n = top_n
        self.score_variance_threshold = score_variance_threshold
        self.min_mean_performance = min_mean_performance
        self.noise_ceiling = noise_ceiling
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

    def _get_top_n_scores(self, dataset: Dataset) -> List[float]:
        """
        Get scores for top N models for a dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            List of top N scores
        """
        model_data = self._load_model_data()
        eval_name = self.dataset_to_eval_map.get(dataset.name)

        if not eval_name:
            return []

        # Extract scores for this evaluation
        scores = []
        for model in model_data:
            for eval_result in model.get("evaluation_results", []):
                if eval_result["evaluation_name"] == eval_name:
                    scores.append(eval_result["score_details"]["score"])
                    break

        # Sort by score (descending) and get top N
        scores.sort(reverse=True)
        return scores[: self.top_n]

    def _compute(self, dataset: Dataset) -> Dict[str, Union[bool, float, str]]:
        """
        Compute saturation status for a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            Dict containing saturation status and metrics
        """
        top_scores = self._get_top_n_scores(dataset)

        if len(top_scores) < self.top_n:
            return {
                "is_saturated": False,
                "reason": f"Insufficient models (found {len(top_scores)}, need {self.top_n})",
                "top_n_count": len(top_scores),
                "mean_performance": None,
                "score_range": None,
            }

        # Calculate metrics
        max_score = top_scores[0]
        min_score = top_scores[-1]
        score_range = max_score - min_score
        mean_performance = sum(top_scores) / len(top_scores)

        # Check saturation conditions
        condition_1 = score_range <= self.score_variance_threshold
        condition_2 = mean_performance >= self.min_mean_performance
        condition_3 = mean_performance >= (self.noise_ceiling - 2.0)

        is_saturated = condition_1 and condition_2 and condition_3

        # Build reason string
        reasons = []
        if not condition_1:
            reasons.append(
                f"Score range {score_range:.2f}% > {self.score_variance_threshold}%"
            )
        if not condition_2:
            reasons.append(
                f"Mean performance {mean_performance:.2f}% < {self.min_mean_performance}%"
            )
        if not condition_3:
            reasons.append(
                f"Mean performance {mean_performance:.2f}% < noise ceiling - 2% ({self.noise_ceiling - 2.0}%)"
            )

        reason = "Saturated" if is_saturated else "; ".join(reasons)

        return {
            "is_saturated": is_saturated,
            "reason": reason,
            "top_n_count": len(top_scores),
            "mean_performance": round(mean_performance, 2),
            "score_range": round(score_range, 2),
            "max_score": round(max_score, 2),
            "min_score": round(min_score, 2),
            "noise_ceiling": self.noise_ceiling,
            "thresholds": {
                "score_variance": self.score_variance_threshold,
                "min_mean_performance": self.min_mean_performance,
                "noise_ceiling_minus_2": self.noise_ceiling - 2.0,
            },
        }

    def run_on_dataset(self, dataset: Dataset) -> Dict[str, Union[bool, float, str]]:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            Dict containing saturation status and metrics
        """
        return self._compute(dataset)

    def run_on_leaderboard(
        self, leaderboard: Leaderboard
    ) -> Dict[str, Dict[str, Union[bool, float, str]]]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict mapping dataset names to their saturation status
        """
        datasets = leaderboard.datasets
        leaderboard_results = {}

        for dataset_name, dataset in datasets.items():
            dataset_result = self._compute(dataset)
            leaderboard_results[dataset_name] = dataset_result

        return leaderboard_results

    def _compute_current(self, leaderboard: Leaderboard) -> Dict[str, Dict]:
        """
        Compute current saturation status (for UpdatableMetric interface).
        """
        return self.run_on_leaderboard(leaderboard)

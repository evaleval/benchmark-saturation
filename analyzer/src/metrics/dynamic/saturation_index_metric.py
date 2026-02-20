"""
Saturation Index metric for computing statistical saturation of top N models.

This metric computes the saturation index (S_index) for the current top N models
on each benchmark evaluation using the statistical framework.
"""

from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset, Leaderboard
from analyzer.src.metrics.dynamic.saturation_utils import compute_saturation_metrics
from typing import Dict, Union, List
import json


class SaturationIndexMetric(UpdatableMetric):
    """
    Metric to compute saturation index for top N models on a benchmark.
    
    Computes statistical saturation metrics including:
    - S_index: Saturation index (0-1, higher = more saturated)
    - R_norm: Normalized score range
    - SE_delta: Standard error of difference between top and Nth model
    - Saturation category: very_low, low, moderate, high, very_high
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        top_n: int = 5,
        jsonl_path: str = "",
        dataset_to_eval_map: Dict[str, str] = None,
        alpha: float = 0.5,
        z: float = 1.96,
    ):
        """
        Initialize the saturation index metric.
        
        Args:
            name: Metric name
            description: Metric description
            top_n: Number of top models to analyze (default 5)
            jsonl_path: Path to leaderboard JSONL file
            dataset_to_eval_map: Mapping from dataset names to evaluation names
            alpha: Exponent for effective sample size (default 0.5)
            z: Standard normal quantile for confidence (default 1.96 for 95%)
        """
        super().__init__(name, description)
        self.top_n = top_n
        self.jsonl_path = jsonl_path
        self.dataset_to_eval_map = dataset_to_eval_map or {}
        self.alpha = alpha
        self.z = z
        self._model_data = None

    def _load_model_data(self) -> List[dict]:
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
            List of top N scores (sorted descending)
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

    def _compute(self, dataset: Dataset) -> Union[Dict, None]:
        """
        Compute saturation index for a single dataset.
        
        Args:
            dataset: The dataset to analyze
        
        Returns:
            Dict containing saturation metrics, or None if insufficient data
        """
        # Get test set size from dataset
        data = dataset.data
        if data is None:
            return {
                "status": "error",
                "message": "No data available",
                "S_index": None,
                "saturation_category": None,
            }

        test_set_size = int(data.iloc[0]["total_samples"])

        # Get top N scores
        top_scores = self._get_top_n_scores(dataset)

        # Check if we have enough models
        if len(top_scores) < self.top_n:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.top_n} models, found {len(top_scores)}",
                "num_models": len(top_scores),
                "S_index": None,
                "saturation_category": None,
            }

        # Compute saturation metrics
        try:
            metrics = compute_saturation_metrics(
                scores=top_scores,
                test_set_size=test_set_size,
                alpha=self.alpha,
                z=self.z,
            )

            return {
                "status": "success",
                "S_index": metrics["s_index"],
                "saturation_category": metrics["category"],
                "R_norm": metrics["r_norm"],
                "SE_delta": metrics["se_delta"],
                "score_range": metrics["score_range"],
                "mean_score": metrics["mean_score"],
                "s1": metrics["s1"],
                "s5": metrics["s5"],
                "n_eff": metrics["n_eff"],
                "test_set_size": test_set_size,
                "is_statistically_similar": metrics["is_statistically_similar"],
                "num_models": len(top_scores),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error computing metrics: {str(e)}",
                "S_index": None,
                "saturation_category": None,
            }

    def run_on_dataset(self, dataset: Dataset) -> Union[Dict, None]:
        """
        Run the metric on a single dataset.
        
        Args:
            dataset: The dataset to analyze
        
        Returns:
            Dict containing saturation metrics
        """
        return self._compute(dataset)

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, Union[Dict, None]]:
        """
        Run the metric on all datasets in a leaderboard.
        
        Args:
            leaderboard: The leaderboard to analyze
        
        Returns:
            Dict mapping dataset names to their saturation metrics
        """
        datasets = leaderboard.datasets
        leaderboard_results = {}

        for dataset_name, dataset in datasets.items():
            dataset_result = self._compute(dataset)
            leaderboard_results[dataset_name] = dataset_result

        return leaderboard_results

    def _compute_current(self, leaderboard: Leaderboard) -> Dict[str, Dict]:
        """
        Compute current saturation metrics (for UpdatableMetric interface).
        
        Args:
            leaderboard: The leaderboard to analyze
        
        Returns:
            Dict mapping dataset names to their saturation metrics
        """
        return self.run_on_leaderboard(leaderboard)

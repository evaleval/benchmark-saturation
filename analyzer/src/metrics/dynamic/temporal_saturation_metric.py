"""
Temporal saturation metric for tracking saturation evolution over time.

This metric computes saturation indices using sliding windows of models
ordered chronologically by submission date.
"""

from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.base import Dataset
from analyzer.src.metrics.dynamic.saturation_utils import compute_saturation_metrics
from typing import Dict, List, Union, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import os


class TemporalSaturationMetric(UpdatableMetric):
    """
    Metric to track benchmark saturation over time using sliding windows.
    
    For each benchmark evaluation, this metric:
    1. Orders models chronologically by created_at date
    2. Creates sliding windows of N consecutive models
    3. Computes saturation metrics for each window using top-N models until that time
    4. Tracks saturation evolution over time
    5. Persists trajectory data to JSON files
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        jsonl_path: str = "",
        dataset_to_eval_map: Dict[str, str] = None,
        output_dir: str = "results/saturation_trajectories",
        top_n: int = 5,
        alpha: float = 0.5,
        z: float = 1.96,
        sampling_interval: int = 10,
    ):
        """
        Initialize the temporal saturation metric.
        
        Args:
            name: Metric name
            description: Metric description
            jsonl_path: Path to leaderboard JSONL file
            dataset_to_eval_map: Mapping from dataset names to evaluation names
            output_dir: Directory to save trajectory JSON files
            top_n: Number of top models to analyze (default 5)
            alpha: Exponent for effective sample size (default 0.5)
            z: Standard normal quantile for confidence (default 1.96 for 95%)
            sampling_interval: Store every Nth window (default 10)
        """
        super().__init__(name, description)
        self.jsonl_path = jsonl_path
        self.dataset_to_eval_map = dataset_to_eval_map or {}
        self.output_dir = output_dir
        self.top_n = top_n
        self.alpha = alpha
        self.z = z
        self.sampling_interval = sampling_interval
        self._model_data = None
        self._trajectory = []

    def _load_model_data(self) -> List[dict]:
        """Load JSONL file once and cache it."""
        if self._model_data is None:
            self._model_data = []
            with open(self.jsonl_path, "r") as f:
                for line in f:
                    self._model_data.append(json.loads(line))
        return self._model_data

    def _extract_models_with_dates(
        self, eval_name: str
    ) -> tuple[List[dict], List[str]]:
        """
        Extract models for a specific evaluation and separate by created_at date availability.
        
        Args:
            eval_name: Name of the evaluation to filter by
        
        Returns:
            Tuple of (valid_models, skipped_model_ids)
            - valid_models: List of dicts with {model_id, score, created_at, created_at_datetime}
            - skipped_model_ids: List of model IDs without created_at dates
        """
        model_data = self._load_model_data()
        valid_models = []
        skipped_model_ids = []

        for model in model_data:
            model_id = model.get("model_info", {}).get("id", "unknown")
            created_at = model.get("created_at")

            # Find the evaluation result
            eval_result = None
            for result in model.get("evaluation_results", []):
                if result["evaluation_name"] == eval_name:
                    eval_result = result
                    break

            if eval_result is None:
                continue  # Model doesn't have this evaluation

            # Check if created_at date is available
            if not created_at:
                skipped_model_ids.append(model_id)
                continue

            try:
                # Parse created_at date (ISO 8601 format with timezone)
                # Handle both formats: "2025-02-25T07:03:38+00:00" and "2025-02-25T07:03:38Z"
                if created_at.endswith('Z'):
                    created_at_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_at_datetime = datetime.fromisoformat(created_at)
                
                # Strip timezone info for consistent comparison
                created_at_datetime = created_at_datetime.replace(tzinfo=None)
                
                score = eval_result["score_details"]["score"]
                
                # Format date as YYYY-MM-DD for display
                created_at_str = created_at_datetime.strftime("%Y-%m-%d")

                valid_models.append({
                    "model_id": model_id,
                    "score": score,
                    "created_at": created_at_str,
                    "created_at_datetime": created_at_datetime,
                })
            except (ValueError, KeyError) as e:
                # Failed to parse date or extract score
                skipped_model_ids.append(model_id)

        # Sort valid models by created_at date
        valid_models.sort(key=lambda m: m["created_at_datetime"])

        return valid_models, skipped_model_ids

    def _compute_sliding_windows(
        self,
        valid_models: List[dict],
        test_set_size: int,
    ) -> tuple[List[dict], Optional[float], Optional[int]]:
        """
        Compute saturation metrics for sliding windows using cumulative top-N models.
        
        For each sliding window of N consecutive submissions, compute S_index using
        the top-N models created until that time point.
        
        Args:
            valid_models: List of models sorted by created_at date (earliest first)
            test_set_size: Size of the test set for this evaluation
        
        Returns:
            Tuple of (trajectory, months_to_saturation, saturation_window_idx):
            - trajectory: List of window result dictionaries (sampled according to sampling_interval)
            - months_to_saturation: Number of months from saturation date to 2026-01-01, or None
            - saturation_window_idx: Index of window where saturation first occurred, or None
        """
        trajectory = []
        months_to_saturation = None
        saturation_date = None
        saturation_window_idx = None
        num_models = len(valid_models)
        reference_date = datetime(2026, 1, 1)  # Fixed reference date

        if num_models < self.top_n:
            return trajectory, months_to_saturation, saturation_window_idx

        # Create sliding windows (overlapping groups of top_n)
        for window_idx in range(num_models - self.top_n + 1):
            # Window end is at position window_idx + top_n - 1
            window_end_idx = window_idx + self.top_n - 1
            
            # Get ALL models submitted until this time point (from 0 to window_end_idx)
            models_until_now = valid_models[: window_end_idx + 1]
            
            # Extract scores and sort to get top-N performers
            all_scores_until_now = [m["score"] for m in models_until_now]
            all_scores_until_now.sort(reverse=True)
            
            # Take top-N scores
            top_n_scores = all_scores_until_now[:self.top_n]

            # Compute saturation metrics for these top-N models
            metrics = compute_saturation_metrics(
                scores=top_n_scores,
                test_set_size=test_set_size,
                alpha=self.alpha,
                z=self.z,
            )
            
            # Check for time-to-saturation (S_index >= 0.7 for the first time)
            if saturation_date is None and metrics["s_index"] >= 0.7:
                saturation_date = models_until_now[-1]["created_at_datetime"]
                saturation_window_idx = window_idx
                # Calculate months between saturation date and reference date (2026-01-01)
                delta = relativedelta(reference_date, saturation_date)
                months_to_saturation = delta.years * 12 + delta.months + (delta.days / 30.0)

            # Determine which windows to store
            should_store = (
                window_idx % self.sampling_interval == 0 or  # Regular sampling
                window_idx == num_models - self.top_n or     # Last window
                window_idx == saturation_window_idx          # ALWAYS store saturation window
            )

            if should_store:
                # Get the actual window models for metadata
                window_models = valid_models[window_idx : window_idx + self.top_n]
                
                window_result = {
                    "window_index": window_idx,
                    "window_start_date": window_models[0]["created_at"],
                    "window_end_date": window_models[-1]["created_at"],
                    "cumulative_end_date": models_until_now[-1]["created_at"],
                    "num_models_until_now": len(models_until_now),
                    "top_n": self.top_n,
                    "top_n_scores": top_n_scores,
                    "mean_score": metrics["mean_score"],
                    "s1": metrics["s1"],
                    "s5": metrics["s5"],
                    "score_range": metrics["score_range"],
                    "S_index": metrics["s_index"],
                    "R_norm": metrics["r_norm"],
                    "SE_delta": metrics["se_delta"],
                    "saturation_category": metrics["category"],
                    "n_eff": metrics["n_eff"],
                    "test_set_size": test_set_size,
                    "is_statistically_similar": metrics["is_statistically_similar"],
                    "is_saturation_window": (window_idx == saturation_window_idx),  # Mark saturation window
                }
                trajectory.append(window_result)

        return trajectory, months_to_saturation, saturation_window_idx

    def _persist_trajectory(
        self,
        eval_name: str,
        trajectory: List[dict],
        total_windows: int,
        num_skipped_models: int,
        skipped_model_ids: List[str],
        months_to_saturation: Optional[float],
        saturation_window_idx: Optional[int],
    ) -> str:
        """
        Save trajectory data to a JSON file.
        
        Args:
            eval_name: Name of the evaluation
            trajectory: List of window results
            total_windows: Total number of windows computed
            num_skipped_models: Number of models without submission dates
            skipped_model_ids: IDs of skipped models
            months_to_saturation: Number of months from saturation to 2026-01-01, or None
        
        Returns:
            Path to the saved JSON file
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Build the output structure
        output_data = {
            "metadata": {
                "evaluation_name": eval_name,
                "total_windows": total_windows,
                "sampled_windows": len(trajectory),
                "sampling_interval": self.sampling_interval,
                "top_n": self.top_n,
                "alpha": self.alpha,
                "z": self.z,
                "num_skipped_models": num_skipped_models,
                "skipped_model_ids": skipped_model_ids,
                "months_to_saturation": months_to_saturation,
                "saturation_window_index": saturation_window_idx,
                "saturation_threshold": 0.7,
                "reference_date": "2026-01-01",
                "generated_at": datetime.now().isoformat(),
            },
            "trajectory": trajectory,
        }

        # Save to file
        filename = f"{eval_name.replace(' ', '_')}_saturation_trajectory.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(output_data, f, indent=2)

        return filepath

    def _compute(self, dataset: Dataset) -> Union[Dict, None]:
        """
        Compute temporal saturation metrics for a single dataset.
        
        Args:
            dataset: The dataset to analyze
        
        Returns:
            Dict containing latest saturation metrics and metadata, or None if insufficient data
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

        # Get evaluation name for JSONL lookup
        eval_name = self.dataset_to_eval_map.get(dataset.name)
        if not eval_name:
            return {
                "status": "error",
                "message": f"No evaluation mapping found for dataset {dataset.name}",
                "S_index": None,
                "saturation_category": None,
            }

        # Extract and filter models
        valid_models, skipped_model_ids = self._extract_models_with_dates(eval_name)

        # Check if we have enough models
        if len(valid_models) < self.top_n:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.top_n} models with submission dates, found {len(valid_models)}",
                "num_valid_models": len(valid_models),
                "num_skipped_models": len(skipped_model_ids),
                "S_index": None,
                "saturation_category": None,
            }

        # Compute sliding windows
        trajectory, months_to_saturation, saturation_window_idx = self._compute_sliding_windows(
            valid_models, test_set_size
        )

        # Calculate total windows
        total_windows = len(valid_models) - self.top_n + 1

        # Persist trajectory to JSON
        trajectory_file = self._persist_trajectory(
            eval_name=eval_name,
            trajectory=trajectory,
            total_windows=total_windows,
            num_skipped_models=len(skipped_model_ids),
            skipped_model_ids=skipped_model_ids,
            months_to_saturation=months_to_saturation,
            saturation_window_idx=saturation_window_idx,
        )

        # Return summary metrics (latest window)
        if trajectory:
            latest_window = trajectory[-1]
            return {
                "status": "success",
                "S_index": latest_window["S_index"],
                "saturation_category": latest_window["saturation_category"],
                "R_norm": latest_window["R_norm"],
                "SE_delta": latest_window["SE_delta"],
                "score_range": latest_window["score_range"],
                "mean_score": latest_window["mean_score"],
                "s1": latest_window["s1"],
                "s5": latest_window["s5"],
                "num_windows_computed": total_windows,
                "num_sampled_windows": len(trajectory),
                "num_skipped_models": len(skipped_model_ids),
                "num_valid_models": len(valid_models),
                "date_range_covered": f"{valid_models[0]['created_at']} to {valid_models[-1]['created_at']}",
                "latest_created_at": latest_window["window_end_date"],
                "months_to_saturation": months_to_saturation,
                "test_set_size": test_set_size,
                "n_eff": latest_window["n_eff"],
                "trajectory_file_path": trajectory_file,
            }
        else:
            return {
                "status": "error",
                "message": "No trajectory windows computed",
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

    def run_on_leaderboard(self, leaderboard) -> Dict[str, Union[Dict, None]]:
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

    def _compute_current(self, leaderboard) -> Dict[str, Dict]:
        """
        Compute current saturation metrics (for UpdatableMetric interface).
        
        Args:
            leaderboard: The leaderboard to analyze
        
        Returns:
            Dict mapping dataset names to their saturation metrics
        """
        return self.run_on_leaderboard(leaderboard)

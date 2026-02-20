from typing import Dict, Union
from analyzer.src.metrics.base import Metric, Dataset, Leaderboard


class UpdatableMetric(Metric):
    """
    Abstract base class for updatable metrics.

    Updatable metrics are computed periodically and track historical values
    over time. They may depend on external data sources that change.
    """

    def __init__(
        self, name: str, description: str = "", update_frequency_days: int = 7
    ):
        super().__init__(name, description)
        self.update_frequency_days = update_frequency_days
        self._historical_values: Dict[str, Dict[str, float]] = (
            {}
        )  # dataset_id -> {timestamp: value}

    def run(self, target: Union[Dataset, Leaderboard]) -> float:
        """
        Run the updatable metric on a dataset or leaderboard.

        Args:
            target: The dataset or leaderboard to analyze

        Returns:
            float: The current metric score
        """
        target_id = self._get_target_id(target)
        current_value = self._compute_current(target)

        # Store the historical value
        if target_id not in self._historical_values:
            self._historical_values[target_id] = {}

        import datetime

        timestamp = datetime.datetime.now().isoformat()
        self._historical_values[target_id][timestamp] = current_value

        return current_value

    def _compute_current(self, target: Union[Dataset, Leaderboard]) -> float:
        """
        Compute the current value of the updatable metric.

        Args:
            target: The dataset or leaderboard to analyze

        Returns:
            Union[float, str]: The current metric score
        """
        raise NotImplementedError("Subclasses must implement _compute_current")

    def get_historical_values(self, target: Union[Dataset, Leaderboard]) -> Dict[str, float]:
        """
        Get historical values for a dataset or leaderboard.

        Args:
            target: The dataset or leaderboard

        Returns:
            Dict[str, float]: Historical values with timestamps as keys
        """
        target_id = self._get_target_id(target)
        return self._historical_values.get(target_id, {})

    def _get_target_id(self, target: Union[Dataset, Leaderboard]) -> str:
        """
        Get a unique identifier for the target dataset or leaderboard.

        Args:
            target: The dataset or leaderboard

        Returns:
            str: Unique identifier
        """
        # Default implementation - subclasses can override
        return f"{target.__class__.__name__}_{id(target)}"

    def needs_update(self, target: Union[Dataset, Leaderboard]) -> bool:
        """
        Check if the metric needs to be updated for this dataset or leaderboard.

        Args:
            target: The dataset or leaderboard

        Returns:
            bool: True if update is needed
        """
        # Simple implementation - can be overridden for more sophisticated logic
        import datetime

        target_id = self._get_target_id(target)

        if target_id not in self._historical_values:
            return True

        if not self._historical_values[target_id]:
            return True

        # Check if the last update was more than update_frequency_days ago
        last_timestamp = max(self._historical_values[target_id].keys())
        last_update = datetime.datetime.fromisoformat(last_timestamp)
        days_since_update = (datetime.datetime.now() - last_update).days

        return days_since_update >= self.update_frequency_days

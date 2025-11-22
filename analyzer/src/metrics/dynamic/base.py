from typing import Dict, Union
from analyzer.src.metrics.base import Metric, Leaderboard


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
        )  # leaderboard_id -> {timestamp: value}

    def run(self, leaderboard: Leaderboard) -> float:
        """
        Run the updatable metric on a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            float: The current metric score
        """
        leaderboard_id = self._get_leaderboard_id(leaderboard)
        current_value = self._compute_current(leaderboard)

        # Store the historical value
        if leaderboard_id not in self._historical_values:
            self._historical_values[leaderboard_id] = {}

        import datetime

        timestamp = datetime.datetime.now().isoformat()
        self._historical_values[leaderboard_id][timestamp] = current_value

        return current_value

    def _compute_current(self, leaderboard: Leaderboard) -> Union[float, str]:
        """
        Compute the current value of the updatable metric.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Union[float, str]: The current metric score
        """
        raise NotImplementedError("Subclasses must implement _compute_current")

    def get_historical_values(self, leaderboard: Leaderboard) -> Dict[str, float]:
        """
        Get historical values for a leaderboard.

        Args:
            leaderboard: The leaderboard

        Returns:
            Dict[str, float]: Historical values with timestamps as keys
        """
        leaderboard_id = self._get_leaderboard_id(leaderboard)
        return self._historical_values.get(leaderboard_id, {})

    def _get_leaderboard_id(self, leaderboard: Leaderboard) -> str:
        """
        Get a unique identifier for the leaderboard.

        Args:
            leaderboard: The leaderboard

        Returns:
            str: Unique identifier
        """
        # Default implementation - subclasses can override
        return f"{leaderboard.__class__.__name__}_{id(leaderboard)}"

    def needs_update(self, leaderboard: Leaderboard) -> bool:
        """
        Check if the metric needs to be updated for this leaderboard.

        Args:
            leaderboard: The leaderboard

        Returns:
            bool: True if update is needed
        """
        # Simple implementation - can be overridden for more sophisticated logic
        import datetime

        leaderboard_id = self._get_leaderboard_id(leaderboard)

        if leaderboard_id not in self._historical_values:
            return True

        if not self._historical_values[leaderboard_id]:
            return True

        # Check if the last update was more than update_frequency_days ago
        last_timestamp = max(self._historical_values[leaderboard_id].keys())
        last_update = datetime.datetime.fromisoformat(last_timestamp)
        days_since_update = (datetime.datetime.now() - last_update).days

        return days_since_update >= self.update_frequency_days

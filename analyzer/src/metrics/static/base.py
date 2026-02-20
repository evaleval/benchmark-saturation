from typing import Dict
from analyzer.src.metrics.base import Metric, Leaderboard
from typing import Union


class StaticMetric(Metric):
    """
    Abstract base class for static metrics.

    Static metrics are computed once when a benchmark is added and
    their values don't change over time.
    """

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self._computed_values: Dict[str, float] = {}

    def run(self, leaderboard: Leaderboard) -> float:
        """
        Run the static metric on a benchmark.

        Args:
            benchmark: The benchmark to analyze

        Returns:
            float: The static metric score
        """
        # Check if we've already computed this value
        leaderboard_id = self._get_leaderboard_id(leaderboard)
        if leaderboard_id in self._computed_values:
            return self._computed_values[leaderboard_id]

        # Compute the value
        score = self._compute(leaderboard)
        self._computed_values[leaderboard_id] = score
        return score

    def _compute(self, leaderboard: Leaderboard) -> Union[float, str]:
        """
        Compute the static metric value.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            float: The computed metric score
        """
        raise NotImplementedError("Subclasses must implement _compute")

    def _get_leaderboard_id(self, leaderboard: Leaderboard) -> str:
        """
        Get a unique identifier for the benchmark.

        Args:
            leaderboard: The leaderboard

        Returns:
            str: Unique identifier
        """
        # Default implementation - subclasses can override
        return f"{leaderboard.__class__.__name__}_{id(leaderboard)}"

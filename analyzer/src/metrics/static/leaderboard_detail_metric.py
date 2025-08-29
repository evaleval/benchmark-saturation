from static.base import StaticMetric
from analyzer.src.metrics.base import Benchmark
from typing import Union


class LeaderboardDetailMetric(StaticMetric):
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)

    def _compute(self, benchmark: Benchmark) -> Union[float, str]:
        data = benchmark.data
        if data is None:
            return "No data available"

        return data.iloc[0][
            "leaderboard_detail"
        ]  # Format will be leaderboard_name and link to leaderboard

    def run(self, benchmark: Benchmark) -> Union[float, str]:
        return self._compute(benchmark)

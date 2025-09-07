from static.base import StaticMetric
from analyzer.src.metrics.base import Benchmark
from typing import Union


class EvaluationMetric(StaticMetric):
    """
    EvaluationMetric (metric used for evaluation of the dataset benchmark, e.g. BLEU, F1 etc) for these datasets.
    """

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)

    def _compute(self, benchmark: Benchmark) -> Union[float, str]:
        data = benchmark.data
        if data is None:
            return "No data available"

        return data.iloc[0]["eval_metrics"]

    def run(self, benchmark: Benchmark) -> Union[float, str]:
        return self._compute(benchmark)

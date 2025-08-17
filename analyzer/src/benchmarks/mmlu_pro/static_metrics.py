from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.benchmarks.mmlu_pro.benchmark import MMLUPro


class NumHFDownloadsMetric(StaticMetric):
    def __init__(self):
        super().__init__('num_hf_downloads', 'Number of Hugging Face downloads')

    def _compute(self, benchmark: MMLUPro) -> float:
        processed_data = benchmark.process(benchmark.data)
        return processed_data['hf_downloads'].sum()
    

class NumHFlikesMetric(StaticMetric):
    def __init__(self):
        super().__init__('num_hf_likes', 'Number of Hugging Face likes')

    def _compute(self, benchmark: MMLUPro) -> float:
        processed_data = benchmark.process(benchmark.data)
        return processed_data['hf_likes'].sum()
    


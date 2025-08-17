#!/usr/bin/env python3
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

from analyzer.src.benchmarks.mmlu_pro.benchmark import MMLUPro
from analyzer.src.benchmarks.mmlu_pro.static_metrics import NumHFDownloadsMetric, NumHFlikesMetric

# Create the benchmark
benchmark = MMLUPro(
    dataset_name="MMLU Pro",
    paper_url="https://example.com/mmlu_pro_paper",
    dataset_url="https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro",
    ds_id="TIGER-Lab/MMLU-Pro"
)

# Refresh the benchmark data
benchmark.refresh()

# Run metrics
static_metrics = [
    NumHFDownloadsMetric(),
    NumHFlikesMetric()
]

print("=== MMLU Pro Metrics Results ===")
for metric in static_metrics:
    try:
        score = metric.run(benchmark)
        print(f"{metric.name}: {score}")
    except Exception as e:
        print(f"Error running {metric.name}: {e}")

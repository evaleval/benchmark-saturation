"""
Test script to run metrics on a single HELM dataset.

This script demonstrates running both static and dynamic metrics
on a single dataset for testing purposes.
"""

from analyzer.src.metrics.static.modality_detail_metric import ModalityMetric
from analyzer.src.metrics.static.is_public_metric import IsPublicMetric
from analyzer.src.metrics.static.language_metric import LanguageMetric
from analyzer.src.metrics.static.total_len_dataset_metric import TotalLenDatasetMetric
from analyzer.src.metrics.static.task_category_metric import TaskCategoryMetric
from analyzer.src.metrics.static.leaderboard_detail_metric import LeaderboardDetailMetric

from analyzer.src.metrics.dynamic.dataset_downloads_metric import DatasetDownloadsMetric
from analyzer.src.metrics.dynamic.dataset_likes_metric import DatasetLikesMetric
from analyzer.src.metrics.dynamic.dataset_freshness_metric import DatasetFreshnessMetric
from analyzer.src.metrics.dynamic.trending_score_metric import TrendingScoreMetric

from analyzer.src.leaderboards.helm.banking77 import Banking77Dataset


def test_single_dataset():
    """
    Test metrics on the banking77 dataset only.
    """
    
    print("=" * 60)
    print("Testing HELM Banking77 Dataset")
    print("=" * 60)
    
    # Initialize the dataset
    banking77_dataset = Banking77Dataset(
        name="banking77",
        paper_url="https://arxiv.org/abs/2003.04807",
        dataset_url="https://huggingface.co/datasets/mteb/banking77",
        hf_dataset_id="mteb/banking77",
        static_data_path="data/helm_dataset_metadata.json",
    )
    
    # Download and process metadata
    print("\n[1/3] Loading metadata...")
    try:
        metadata = banking77_dataset.download()
        dataset_key = "mteb/banking77"
        
        if "datasets" in metadata and dataset_key in metadata["datasets"]:
            dataset_data = metadata["datasets"][dataset_key]
            banking77_dataset.process(dataset_data)
            print("✓ Metadata loaded successfully")
            print(f"  - Dataset ID: {dataset_key}")
            print(f"  - Benchmark: {dataset_data.get('benchmark', 'N/A')}")
        else:
            print(f"✗ Error: No metadata found for {dataset_key}")
            return
    except Exception as e:
        print(f"✗ Error loading metadata: {e}")
        return
    
    # Define metrics
    static_metrics = [
        TotalLenDatasetMetric(name="total_samples"),
        ModalityMetric(name="modality"),
        LanguageMetric(name="language"),
        IsPublicMetric(name="is_public"),
        LeaderboardDetailMetric(name="leaderboard"),
        TaskCategoryMetric(name="task_categories"),
    ]
    
    dynamic_metrics = [
        DatasetDownloadsMetric(name="downloads"),
        DatasetLikesMetric(name="likes"),
        DatasetFreshnessMetric(name="last_modified"),
        TrendingScoreMetric(name="trending_score"),
    ]
    
    # Run static metrics
    print("\n[2/3] Running Static Metrics...")
    print("-" * 60)
    static_results = {}
    for metric in static_metrics:
        try:
            result = metric.run_on_dataset(banking77_dataset)
            static_results[metric.name] = result
            print(f"  ✓ {metric.name:20s} = {result}")
        except Exception as e:
            print(f"  ✗ {metric.name:20s} ERROR: {e}")
            static_results[metric.name] = None
    
    # Run dynamic metrics
    print("\n[3/3] Running Dynamic Metrics...")
    print("-" * 60)
    dynamic_results = {}
    for metric in dynamic_metrics:
        try:
            result = metric.run_on_dataset(banking77_dataset)
            dynamic_results[metric.name] = result
            print(f"  ✓ {metric.name:20s} = {result}")
        except Exception as e:
            print(f"  ✗ {metric.name:20s} ERROR: {e}")
            dynamic_results[metric.name] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Static Metrics:  {len([v for v in static_results.values() if v is not None])}/{len(static_metrics)} passed")
    print(f"Dynamic Metrics: {len([v for v in dynamic_results.values() if v is not None])}/{len(dynamic_metrics)} passed")
    
    # Show dataset data
    print("\n" + "=" * 60)
    print("Dataset DataFrame Preview")
    print("=" * 60)
    if banking77_dataset.data is not None:
        print(banking77_dataset.data.to_string())
    else:
        print("No data available")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_single_dataset()

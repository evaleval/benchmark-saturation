import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from analyzer.src.metrics.static.modality_detail_metric import ModalityMetric
from analyzer.src.metrics.static.is_public_metric import IsPublicMetric
from analyzer.src.metrics.static.language_metric import LanguageMetric
from analyzer.src.metrics.static.total_len_dataset_metric import TotalLenDatasetMetric
from analyzer.src.metrics.static.task_category_metric import TaskCategoryMetric
from analyzer.src.metrics.static.leaderboard_detail_metric import LeaderboardDetailMetric
from analyzer.src.metrics.static.created_at_metric import CreatedAtMetric

from analyzer.src.metrics.dynamic.dataset_downloads_metric import DatasetDownloadsMetric
from analyzer.src.metrics.dynamic.dataset_likes_metric import DatasetLikesMetric
from analyzer.src.metrics.dynamic.dataset_freshness_metric import DatasetFreshnessMetric
from analyzer.src.metrics.dynamic.trending_score_metric import TrendingScoreMetric
from analyzer.src.metrics.dynamic.top_n_models_metric import TopNModelsMetric
from analyzer.src.metrics.dynamic.saturation_index_metric import SaturationIndexMetric
from analyzer.src.metrics.dynamic.is_saturated_metric import IsSaturatedMetric

from analyzer.src.leaderboards.helm.boolq import BoolQDataset
from analyzer.src.leaderboards.helm.hellaswag import HellaSwagDataset
from analyzer.src.leaderboards.helm.mmlu import MMLUDataset
from analyzer.src.leaderboards.helm.narrativeqa import NarrativeQADataset
from analyzer.src.leaderboards.helm.naturalquestions import NaturalQuestionsDataset
from analyzer.src.leaderboards.helm.openbookqa import OpenBookQADataset
from analyzer.src.leaderboards.helm.quac import QuACDataset
from analyzer.src.leaderboards.helm.truthfulqa import TruthfulQADataset
from analyzer.src.leaderboards.helm.benchmark import HELMLeaderboard


def run_metrics():
    """
    Initialize HELM Classic datasets, load their metadata, and run metrics on them.
    
    HELM Classic scenarios:
    - MMLU (Massive Multitask Language Understanding)
    - BoolQ
    - NarrativeQA
    - NaturalQuestions (closed-book)
    - NaturalQuestions (open-book)
    - QuAC (Question Answering in Context)
    - HellaSwag
    - OpenbookQA
    - TruthfulQA
    """
    
    # Initialize all HELM Classic datasets
    boolq_dataset = BoolQDataset(
        name="boolq",
        paper_url="https://arxiv.org/abs/1905.10044",
        dataset_url="https://huggingface.co/datasets/google/boolq",
        hf_dataset_id="google/boolq",
        static_data_path="data/all_datasets.json",
    )

    hellaswag_dataset = HellaSwagDataset(
        name="hellaswag",
        paper_url="https://arxiv.org/abs/1905.07830",
        dataset_url="https://huggingface.co/datasets/Rowan/hellaswag",
        hf_dataset_id="Rowan/hellaswag",
        static_data_path="data/all_datasets.json",
    )

    mmlu_dataset = MMLUDataset(
        name="mmlu",
        paper_url="https://arxiv.org/abs/2009.03300",
        dataset_url="https://huggingface.co/datasets/cais/mmlu",
        hf_dataset_id="cais/mmlu",
        static_data_path="data/all_datasets.json",
    )

    narrativeqa_dataset = NarrativeQADataset(
        name="narrativeqa",
        paper_url="https://arxiv.org/abs/1712.07040",
        dataset_url="https://huggingface.co/datasets/deepmind/narrativeqa",
        hf_dataset_id="deepmind/narrativeqa",
        static_data_path="data/all_datasets.json",
    )

    # NaturalQuestions closed-book (default config)
    naturalquestions_closed_dataset = NaturalQuestionsDataset(
        name="naturalquestions_closed",
        paper_url="https://arxiv.org/abs/1901.08634",
        dataset_url="https://huggingface.co/datasets/google-research-datasets/natural_questions",
        hf_dataset_id="google-research-datasets/natural_questions",
        static_data_path="data/all_datasets.json",
        config="default",  # closed-book
    )

    # NaturalQuestions open-book (may need different config - adjust based on actual dataset structure)
    naturalquestions_open_dataset = NaturalQuestionsDataset(
        name="naturalquestions_open",
        paper_url="https://arxiv.org/abs/1901.08634",
        dataset_url="https://huggingface.co/datasets/google-research-datasets/natural_questions",
        hf_dataset_id="google-research-datasets/natural_questions",
        static_data_path="data/all_datasets.json",
        config="default",  # TODO: Update with correct open-book config name
    )

    openbookqa_dataset = OpenBookQADataset(
        name="openbookqa",
        paper_url="https://arxiv.org/abs/1809.02789",
        dataset_url="https://huggingface.co/datasets/allenai/openbookqa",
        hf_dataset_id="allenai/openbookqa",
        static_data_path="data/all_datasets.json",
    )

    quac_dataset = QuACDataset(
        name="quac",
        paper_url="https://arxiv.org/abs/1808.07036",
        dataset_url="https://huggingface.co/datasets/allenai/quac",
        hf_dataset_id="allenai/quac",
        static_data_path="data/all_datasets.json",
    )

    truthfulqa_dataset = TruthfulQADataset(
        name="truthfulqa",
        paper_url="https://arxiv.org/abs/2109.07958",
        dataset_url="https://huggingface.co/datasets/domenicrosati/TruthfulQA",
        hf_dataset_id="domenicrosati/TruthfulQA",
        static_data_path="data/all_datasets.json",
    )

    # Download and process metadata for all datasets
    datasets_list = [
        (boolq_dataset, "google/boolq"),
        (hellaswag_dataset, "Rowan/hellaswag"),
        (mmlu_dataset, "cais/mmlu"),
        (narrativeqa_dataset, "deepmind/narrativeqa"),
        (naturalquestions_closed_dataset, "google-research-datasets/natural_questions"),
        (naturalquestions_open_dataset, "google-research-datasets/natural_questions"),  # Same dataset, different config
        (openbookqa_dataset, "allenai/openbookqa"),
        (quac_dataset, "allenai/quac"),
        (truthfulqa_dataset, "domenicrosati/TruthfulQA"),
    ]

    # Create HELM leaderboard
    helm_leaderboard = HELMLeaderboard(
        name="HELM Classic",
        description="Holistic Evaluation of Language Models - Classic benchmark scenarios",
    )

    # Download metadata once (same pattern as hf_openllm_v2)
    # All datasets use the same static_data_path, so download once
    all_datasets = datasets_list[0][0].download() if datasets_list else {}
    print(f"\n=== Loading Metadata ===")
    print(f"Total datasets in all_datasets.json: {len(all_datasets)}")
    
    # Process each dataset
    processed_count = 0
    for dataset_obj, dataset_key in datasets_list:
        try:
            # Access data directly by dataset key (flat structure, matching hf_openllm_v2 pattern)
            # Pattern: all_datasets[dataset_key] instead of all_datasets["datasets"][dataset_key]
            if dataset_key in all_datasets:
                dataset_data = all_datasets[dataset_key]
                dataset_obj.process(dataset_data)
                helm_leaderboard.add_dataset(dataset_obj)
                processed_count += 1
                print(f"✓ Successfully processed {dataset_obj.name} ({dataset_key})")
            else:
                print(f"✗ Warning: No metadata found for {dataset_key}")
        except Exception as e:
            print(f"✗ Error processing {dataset_obj.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Processing Summary ===")
    print(f"Successfully processed: {processed_count}/{len(datasets_list)} datasets")

    # Map HELM dataset names to evaluation names in JSONL
    # Keys MUST match the dataset.name (lowercase identifiers from dataset objects)
    # Values MUST match the evaluation_name in helm_classic_data.jsonl
    dataset_to_eval_map = {
        "boolq": "BoolQ - EM",
        "hellaswag": "HellaSwag - EM",
        "mmlu": "MMLU - EM",
        "narrativeqa": "NarrativeQA - F1",
        "naturalquestions_closed": "NaturalQuestions (closed-book) - F1",
        "naturalquestions_open": "NaturalQuestions (open-book) - F1",
        "openbookqa": "OpenbookQA - EM",
        "quac": "QuAC - F1",
        "truthfulqa": "TruthfulQA - EM",
    }

    # Define static metrics to run
    static_metrics = [
        TotalLenDatasetMetric(name="total_len_dataset"),
        ModalityMetric(name="modality"),
        LanguageMetric(name="language"),
        IsPublicMetric(name="is_public"),
        LeaderboardDetailMetric(name="leaderboard_detail"),
        TaskCategoryMetric(name="task_categories"),
        CreatedAtMetric(name="created_at"),
    ]

    # Define dynamic metrics to run
    dynamic_metrics = [
        DatasetDownloadsMetric(name="dataset_downloads"),
        DatasetLikesMetric(name="dataset_likes"),
        DatasetFreshnessMetric(name="dataset_freshness"),
        TrendingScoreMetric(name="trending_score"),
        TopNModelsMetric(
            name="top_5_models",
            top_n=5,
            jsonl_path="/Users/random/benchmark-saturation/data/leaderboard_data/helm_classic_data.jsonl",
            dataset_to_eval_map=dataset_to_eval_map,
        ),
        IsSaturatedMetric(
            name="is_saturated",
            top_n=5,
            score_variance_threshold=1.0,
            min_mean_performance=95.0,
            noise_ceiling=97.0,
            jsonl_path="/Users/random/benchmark-saturation/data/leaderboard_data/helm_classic_data.jsonl",
            dataset_to_eval_map=dataset_to_eval_map,
        ),
        SaturationIndexMetric(
            name="saturation_index",
            description="Statistical saturation index for top 5 models",
            top_n=5,
            jsonl_path="/Users/random/benchmark-saturation/data/leaderboard_data/helm_classic_data.jsonl",
            dataset_to_eval_map=dataset_to_eval_map,
            alpha=0.5,
            z=1.96,
        ),
    ]

    # Run all metrics on the leaderboard
    all_metric_results = {}
    
    print("\n=== Running Static Metrics ===")
    for metric in static_metrics:
        metric_name = metric.name
        try:
            metric_result = metric.run_on_leaderboard(helm_leaderboard)
            all_metric_results[metric_name] = metric_result
            print(f"✓ {metric_name}")
        except Exception as e:
            print(f"✗ Error running metric {metric_name}: {e}")
            all_metric_results[metric_name] = {"error": str(e)}

    print("\n=== Running Dynamic Metrics ===")
    for metric in dynamic_metrics:
        metric_name = metric.name
        try:
            metric_result = metric.run_on_leaderboard(helm_leaderboard)
            all_metric_results[metric_name] = metric_result
            print(f"✓ {metric_name}")
        except Exception as e:
            print(f"✗ Error running metric {metric_name}: {e}")
            all_metric_results[metric_name] = {"error": str(e)}

    print("\n=== HELM Classic Leaderboard Metrics Results ===")
    for metric_name, results in all_metric_results.items():
        print(f"\n{metric_name}:")
        print(results)

    # Print rankings
    print("\n=== HELM Classic Dataset Rankings ===")
    rankings = helm_leaderboard.compute_rankings()
    print(rankings)

    # Debug: Check if we have any datasets in the leaderboard
    print(f"\n=== Leaderboard Status ===")
    print(f"Number of datasets in leaderboard: {len(helm_leaderboard.datasets)}")
    print(f"Dataset names: {list(helm_leaderboard.datasets.keys())}")
    
    # Debug: Check metric results structure
    print(f"\n=== Metric Results Structure ===")
    for metric_name, metric_result in all_metric_results.items():
        if isinstance(metric_result, dict):
            print(f"{metric_name}: {len(metric_result)} datasets - {list(metric_result.keys())[:5]}")
        else:
            print(f"{metric_name}: {type(metric_result)} - {metric_result}")

    # Export to CSV using pandas
    export_to_csv_pandas(all_metric_results, "metrics_output_helm_classic_updated.csv")

    return all_metric_results


def export_to_csv_pandas(metrics_data, filename):
    """
    Export metrics data to CSV format using pandas.
    Each dataset becomes a row, each metric becomes a column.
    
    Args:
        metrics_data: Dictionary where keys are metric names and values are 
                     dictionaries mapping dataset names to metric values
        filename: Output CSV filename
    """
    # Structure: {metric_name: {dataset_name: value}}
    # We want: dataset_name as rows, metric_name as columns
    
    # Get all unique dataset names from all metrics
    all_datasets = set()
    for metric_result in metrics_data.values():
        if isinstance(metric_result, dict):
            all_datasets.update(metric_result.keys())
    
    if not all_datasets:
        print(f"\n⚠ Warning: No datasets found in metric results!")
        print(f"  Metric results keys: {list(metrics_data.keys())}")
        print(f"  Metric results types: {[type(v) for v in metrics_data.values()]}")
        # Create empty DataFrame with just columns
        df = pd.DataFrame(columns=["dataset"] + list(metrics_data.keys()))
        df.to_csv(filename, index=False)
        print(f"  Created empty CSV with headers only")
        return
    
    # Create list of dictionaries, one per dataset
    rows = []
    for dataset_name in sorted(all_datasets):
        row = {"dataset": dataset_name}
        for metric_name, metric_result in metrics_data.items():
            if isinstance(metric_result, dict):
                value = metric_result.get(dataset_name, None)
                # Convert complex types (list, dict) to JSON strings for CSV compatibility
                if isinstance(value, (list, dict)):
                    import json
                    row[metric_name] = json.dumps(value) if value is not None else None
                else:
                    row[metric_name] = value
            else:
                row[metric_name] = metric_result
        rows.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Export to CSV (pandas will handle None values and string serialization)
    df.to_csv(filename, index=False)

    print(f"\n✓ Metrics exported to {filename}")
    print(f"  DataFrame shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())


if __name__ == "__main__":
    run_metrics()

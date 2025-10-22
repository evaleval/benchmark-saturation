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
from analyzer.src.leaderboards.helm.financebench import FinanceBenchDataset
from analyzer.src.leaderboards.helm.finqa import FinQADataset
from analyzer.src.leaderboards.helm.legalbench import LegalBenchDataset
from analyzer.src.leaderboards.helm.med_qa import MedQADataset
from analyzer.src.leaderboards.helm.narrativeqa import NarrativeQADataset
from analyzer.src.leaderboards.helm.omni_math import OmniMathDataset
from analyzer.src.leaderboards.helm.openbookqa import OpenBookQADataset
from analyzer.src.leaderboards.helm.wildbench import WildBenchDataset
from analyzer.src.leaderboards.helm.wmt14 import WMT14Dataset
from analyzer.src.leaderboards.helm.benchmark import HELMLeaderboard


def run_metrics():
    """
    Initialize HELM datasets, load their metadata, and run metrics on them.
    """
    
    # Initialize all HELM datasets
    banking77_dataset = Banking77Dataset(
        name="banking77",
        paper_url="https://arxiv.org/abs/2003.04807",
        dataset_url="https://huggingface.co/datasets/mteb/banking77",
        hf_dataset_id="mteb/banking77",
        static_data_path="data/helm_dataset_metadata.json",
    )

    financebench_dataset = FinanceBenchDataset(
        name="financebench",
        paper_url="https://arxiv.org/abs/2311.11944",
        dataset_url="https://huggingface.co/datasets/PatronusAI/financebench",
        hf_dataset_id="PatronusAI/financebench",
        static_data_path="data/helm_dataset_metadata.json",
    )

    finqa_dataset = FinQADataset(
        name="finqa",
        paper_url="",
        dataset_url="https://huggingface.co/datasets/ibm-research/finqa",
        hf_dataset_id="ibm-research/finqa",
        static_data_path="data/helm_dataset_metadata.json",
    )

    legalbench_dataset = LegalBenchDataset(
        name="legalbench",
        paper_url="https://arxiv.org/abs/2308.11462",
        dataset_url="https://huggingface.co/datasets/nguha/legalbench",
        hf_dataset_id="nguha/legalbench",
        static_data_path="data/helm_dataset_metadata.json",
    )

    medqa_dataset = MedQADataset(
        name="med_qa",
        paper_url="",
        dataset_url="https://huggingface.co/datasets/bigbio/med_qa",
        hf_dataset_id="bigbio/med_qa",
        static_data_path="data/helm_dataset_metadata.json",
    )

    narrativeqa_dataset = NarrativeQADataset(
        name="narrativeqa",
        paper_url="https://arxiv.org/abs/1712.07040",
        dataset_url="https://huggingface.co/datasets/deepmind/narrativeqa",
        hf_dataset_id="deepmind/narrativeqa",
        static_data_path="data/helm_dataset_metadata.json",
    )

    omnimath_dataset = OmniMathDataset(
        name="omni_math",
        paper_url="https://arxiv.org/abs/2410.07985",
        dataset_url="https://huggingface.co/datasets/KbsdJames/Omni-MATH",
        hf_dataset_id="KbsdJames/Omni-MATH",
        static_data_path="data/helm_dataset_metadata.json",
    )

    openbookqa_dataset = OpenBookQADataset(
        name="openbookqa",
        paper_url="",
        dataset_url="https://huggingface.co/datasets/allenai/openbookqa",
        hf_dataset_id="allenai/openbookqa",
        static_data_path="data/helm_dataset_metadata.json",
    )

    wildbench_dataset = WildBenchDataset(
        name="wildbench",
        paper_url="https://arxiv.org/abs/2406.04770",
        dataset_url="https://huggingface.co/datasets/allenai/WildBench",
        hf_dataset_id="allenai/WildBench",
        static_data_path="data/helm_dataset_metadata.json",
    )

    wmt14_dataset = WMT14Dataset(
        name="wmt14",
        paper_url="",
        dataset_url="https://huggingface.co/datasets/wmt/wmt14",
        hf_dataset_id="wmt/wmt14",
        static_data_path="data/helm_dataset_metadata.json",
    )

    # Download and process metadata for all datasets
    datasets_list = [
        (banking77_dataset, "mteb/banking77"),
        (financebench_dataset, "PatronusAI/financebench"),
        (finqa_dataset, "ibm-research/finqa"),
        (legalbench_dataset, "nguha/legalbench"),
        (medqa_dataset, "bigbio/med_qa"),
        (narrativeqa_dataset, "deepmind/narrativeqa"),
        (omnimath_dataset, "KbsdJames/Omni-MATH"),
        (openbookqa_dataset, "allenai/openbookqa"),
        (wildbench_dataset, "allenai/WildBench"),
        (wmt14_dataset, "wmt/wmt14"),
    ]

    # Create HELM leaderboard
    helm_leaderboard = HELMLeaderboard(
        name="HELM",
        description="Holistic Evaluation of Language Models benchmark suite",
    )

    # Process each dataset
    for dataset_obj, dataset_key in datasets_list:
        try:
            metadata = dataset_obj.download()
            if "datasets" in metadata and dataset_key in metadata["datasets"]:
                dataset_data = metadata["datasets"][dataset_key]
                dataset_obj.process(dataset_data)
                helm_leaderboard.add_dataset(dataset_obj)
                print(f"Successfully processed {dataset_obj.name}")
            else:
                print(f"Warning: No metadata found for {dataset_key}")
        except Exception as e:
            print(f"Error processing {dataset_obj.name}: {e}")

    # Define static metrics to run
    static_metrics = [
        TotalLenDatasetMetric(name="total_len_dataset"),
        ModalityMetric(name="modality"),
        LanguageMetric(name="language"),
        IsPublicMetric(name="is_public"),
        LeaderboardDetailMetric(name="leaderboard_detail"),
        TaskCategoryMetric(name="task_categories"),
    ]

    # Define dynamic metrics to run
    dynamic_metrics = [
        DatasetDownloadsMetric(name="dataset_downloads"),
        DatasetLikesMetric(name="dataset_likes"),
        DatasetFreshnessMetric(name="dataset_freshness"),
        TrendingScoreMetric(name="trending_score"),
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

    print("\n=== HELM Leaderboard Metrics Results ===")
    for metric_name, results in all_metric_results.items():
        print(f"\n{metric_name}:")
        print(results)

    # Print rankings
    print("\n=== HELM Dataset Rankings ===")
    rankings = helm_leaderboard.compute_rankings()
    print(rankings)

    return all_metric_results


if __name__ == "__main__":
    run_metrics()

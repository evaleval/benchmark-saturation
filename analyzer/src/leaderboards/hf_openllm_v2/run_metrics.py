import pandas as pd
from analyzer.src.metrics.static.modality_detail_metric import ModalityMetric
from analyzer.src.metrics.static.is_public_metric import IsPublicMetric
from analyzer.src.metrics.static.language_metric import LanguageMetric
from analyzer.src.metrics.static.total_len_dataset_metric import TotalLenDatasetMetric
from analyzer.src.metrics.static.task_category_metric import TaskCategoryMetric
from analyzer.src.metrics.static.created_at_metric import CreatedAtMetric
from analyzer.src.metrics.dynamic.top_n_models_metric import TopNModelsMetric
from analyzer.src.metrics.dynamic.is_saturated_metric import IsSaturatedMetric
from analyzer.src.metrics.dynamic.citation_metric import CitationMetric
from analyzer.src.metrics.static.leaderboard_detail_metric import (
    LeaderboardDetailMetric,
)
from analyzer.src.leaderboards.hf_openllm_v2.bigbench_hard_dataset import (
    BigBenchHardDataset,
)
from analyzer.src.leaderboards.hf_openllm_v2.benchmark import HFOpenLLMVB2Leaderboard
from analyzer.src.leaderboards.hf_openllm_v2.gpqa_dataset import GPQADataset
from analyzer.src.leaderboards.hf_openllm_v2.mmlu_pro_dataset import MMLUProDataset
from analyzer.src.leaderboards.hf_openllm_v2.musr_dataset import MUSRDataset
from analyzer.src.leaderboards.hf_openllm_v2.ifeval_dataset import IFEvalDataset
from analyzer.src.leaderboards.hf_openllm_v2.hendrycks_math_dataset import (
    HendrycksMathDataset,
)


def run_metrics():

    bigbench_hard_dataset = BigBenchHardDataset(
        name="bigbench_hard",
        paper_url="https://www.semanticscholar.org/paper/Challenging-BIG-Bench-Tasks-and-Whether-Can-Solve-Suzgun-Scales/663a41c866d49ce052801fbc88947d39764cad29",
        dataset_url="https://huggingface.co/datasets/maveriq/bigbenchhard",
        hf_dataset_id="maveriq/bigbenchhard",
        static_data_path="data/all_datasets.json",
    )

    bigbench_static_data = bigbench_hard_dataset.download()["maveriq/bigbenchhard"]
    bigbench_hard_dataset.process(bigbench_static_data)

    gpqa_dataset = GPQADataset(
        name="gpqa",
        paper_url="https://www.semanticscholar.org/paper/GPQA%3A-A-Graduate-Level-Google-Proof-Q%26A-Benchmark-Rein-Hou/210b0a3d76e93079cc51b03c4115fde545eea966",
        dataset_url="https://huggingface.co/datasets/Idavidrein/gpqa",
        hf_dataset_id="Idavidrein/gpqa",
        static_data_path="data/all_datasets.json",
    )
    gpqa_static_data = gpqa_dataset.download().get("Idavidrein/gpqa", {})
    gpqa_dataset.process(gpqa_static_data)

    mmlu_pro_dataset = MMLUProDataset(
        name="mmlu_pro",
        paper_url="https://www.semanticscholar.org/paper/MMLU-Pro%3A-A-More-Robust-and-Challenging-Multi-Task-Wang-Ma/1406bb4cb6801bc4767b661308118c888a9b09da",
        dataset_url="https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro",
        hf_dataset_id="TIGER-Lab/MMLU-Pro",
        static_data_path="data/all_datasets.json",
    )
    mmlu_pro_static_data = mmlu_pro_dataset.download()["TIGER-Lab/MMLU-Pro"]
    mmlu_pro_dataset.process(mmlu_pro_static_data)

    musr_dataset = MUSRDataset(
        name="musr",
        paper_url="https://www.semanticscholar.org/paper/MuSR%3A-Testing-the-Limits-of-Chain-of-thought-with-Sprague-Ye/743ef29a9406c44c835684c7755d423d6ca0b663",
        dataset_url="https://huggingface.co/datasets/TAUR-Lab/MuSR",
        hf_dataset_id="TAUR-Lab/MuSR",
        static_data_path="data/all_datasets.json",
    )

    musr_static_data = musr_dataset.download()["TAUR-Lab/MuSR"]
    musr_dataset.process(musr_static_data)

    ifeval_dataset = IFEvalDataset(
        name="ifeval",
        paper_url="https://www.semanticscholar.org/paper/Instruction-Following-Evaluation-for-Large-Language-Zhou-Lu/1a9b8c545ba9a6779f202e04639c2d67e6d34f63",
        dataset_url="https://huggingface.co/datasets/TAUR-Lab/MuSR",
        hf_dataset_id="google/IFEval",
        static_data_path="data/all_datasets.json",
    )
    ifeval_static_data = ifeval_dataset.download()["google/IFEval"]
    ifeval_dataset.process(ifeval_static_data)

    hendrycks_math_dataset = HendrycksMathDataset(
        name="hendrycks_math",
        paper_url="https://www.semanticscholar.org/paper/Measuring-Mathematical-Problem-Solving-With-the-Hendrycks-Burns/57d1e7ac339e783898f2c3b1af55737cbeee9fc5",
        dataset_url="https://huggingface.co/datasets/EleutherAI/hendrycks_math",
        hf_dataset_id="EleutherAI/hendrycks_math",
        static_data_path="data/all_datasets.json",
    )
    hendrycks_math_static_data = hendrycks_math_dataset.download()[
        "EleutherAI/hendrycks_math"
    ]
    hendrycks_math_dataset.process(hendrycks_math_static_data)

    leaderboard = HFOpenLLMVB2Leaderboard(
        name="hf_openllm_v2",
        paper_url="https://arxiv.org/abs/2210.09261",
        dataset_url="https://huggingface.co/datasets/maveriq/bigbenchhard",
        hf_dataset_id="maveriq/bigbenchhard",
    )

    leaderboard.add_dataset(bigbench_hard_dataset)
    leaderboard.add_dataset(gpqa_dataset)
    leaderboard.add_dataset(mmlu_pro_dataset)
    leaderboard.add_dataset(musr_dataset)
    leaderboard.add_dataset(ifeval_dataset)
    leaderboard.add_dataset(hendrycks_math_dataset)

    # This is for the TopNModelsMetric and IsSaturatedMetric to map dataset names to eval names
    dataset_to_eval_map = {
        "bigbench_hard": "BBH",
        "gpqa": "GPQA",
        "mmlu_pro": "MMLU-PRO",
        "musr": "MUSR",
        "ifeval": "IFEval",
        "hendrycks_math": "MATH Level 5",
    }

    all_metrics = [
        TotalLenDatasetMetric(name="total_len_dataset"),
        ModalityMetric(name="modality"),
        LanguageMetric(name="language"),
        IsPublicMetric(name="is_public"),
        LeaderboardDetailMetric(name="leaderboard_detail"),
        TaskCategoryMetric(name="task_categories"),
        CreatedAtMetric(name="created_at"),
        TopNModelsMetric(
            name="top_5_models",
            top_n=5,
            jsonl_path="/Users/random/benchmark-saturation/data/leaderboard_data/hfopenllm_v2_data.jsonl",  # Update this path
            dataset_to_eval_map=dataset_to_eval_map,
        ),
        IsSaturatedMetric(
            name="is_saturated",
            top_n=5,
            score_variance_threshold=1.0,
            min_mean_performance=95.0,
            noise_ceiling=97.0,
            jsonl_path="/Users/random/benchmark-saturation/data/leaderboard_data/hfopenllm_v2_data.jsonl",  # Update this path
            dataset_to_eval_map=dataset_to_eval_map,
        ),
        # CitationMetric(
        #     name="citation_count",
        # ),
    ]
    all_metric_results = {}
    for metric in all_metrics:
        metric_name = metric.name
        metric_result = metric.run_on_leaderboard(leaderboard)
        all_metric_results[metric_name] = metric_result

    print(all_metric_results)

    # Export to CSV using pandas
    export_to_csv_pandas(all_metric_results, "metrics_output_hf_llm_v2.csv")

    return all_metric_results


def export_to_csv_pandas(metrics_data, filename):
    """
    Export metrics data to CSV format using pandas.
    Each dataset becomes a row, each metric becomes a column.
    """
    # Convert nested dictionary to DataFrame
    df = pd.DataFrame(metrics_data)

    # Reset index to make dataset names a column
    df = df.reset_index()
    df.columns = ["dataset"] + list(df.columns[1:])

    # Export to CSV
    df.to_csv(filename, index=False)

    print(f"Metrics exported to {filename}")
    print(f"DataFrame shape: {df.shape}")
    print("\nFirst few rows:")
    print(df.head())


if __name__ == "__main__":
    run_metrics()

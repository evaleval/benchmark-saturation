from analyzer.src.metrics.static.modality_detail_metric import ModalityMetric
from analyzer.src.metrics.static.is_public_metric import IsPublicMetric
from analyzer.src.metrics.static.language_metric import LanguageMetric
from analyzer.src.metrics.static.total_len_dataset_metric import TotalLenDatasetMetric
from analyzer.src.metrics.static.leaderboard_detail_metric import LeaderboardDetailMetric
from analyzer.src.leaderboards.hf_openllm_v2.bigbench_hard_dataset import BigBenchHard
from analyzer.src.leaderboards.hf_openllm_v2.benchmark import HFOpenLLMVB2Leaderboard
from analyzer.src.leaderboards.hf_openllm_v2.gpqa_dataset import GPQADataset
from analyzer.src.leaderboards.hf_openllm_v2.mmlu_pro_dataset import MMLUProDataset
from analyzer.src.leaderboards.hf_openllm_v2.musr_dataset import MUSDDataset
from analyzer.src.leaderboards.hf_openllm_v2.ifeval_dataset import IFEvalDataset
from analyzer.src.leaderboards.hf_openllm_v2.hendrycks_math_dataset import HendrycksMathDataset


def run_metrics():

    bigbench_hard_dataset = BigBenchHard(
        name="bigbench_hard",
        paper_url="https://arxiv.org/abs/2210.09261",
        dataset_url="https://huggingface.co/datasets/maveriq/bigbenchhard",
        hf_dataset_id="maveriq/bigbenchhard",
        static_data_path="data/all_datasets.json",
    )


    static_data = bigbench_hard_dataset.download()['maveriq/bigbenchhard']
    bigbench_hard_dataset.process(static_data)

    leaderboard = HFOpenLLMVB2Leaderboard(
        name="hf_openllm_v2",
        paper_url="https://arxiv.org/abs/2210.09261",
        dataset_url="https://huggingface.co/datasets/maveriq/bigbenchhard",
        hf_dataset_id="maveriq/bigbenchhard",
    )

    leaderboard.add_dataset(bigbench_hard_dataset)

    all_metrics = [
        TotalLenDatasetMetric(name='total_len_dataset'),
        ModalityMetric(name='modality'),
        LanguageMetric(name='language'),
        IsPublicMetric(name='is_public'),
        LeaderboardDetailMetric(name='leaderboard_detail'),
    ]
    all_metric_results = {}
    for metric in all_metrics:
        metric_name = metric.name
        metric_result = metric.run_on_leaderboard(leaderboard)
        all_metric_results[metric_name] = metric_result
    print(all_metric_results)
    

if __name__ == "__main__":
    run_metrics()





from analyzer.src.metrics.base import Dataset
from typing import Optional, Any, Dict
import json
import pandas as pd
from datasets import get_dataset_config_info
from datetime import datetime


"""
This dataset is not public on HF, we require a HF key to download it.

"""


class GPQADataset(Dataset):
    def __init__(
        self, name: str, paper_url: str, dataset_url: str, hf_dataset_id: str, **kwargs
    ):
        super().__init__(name, paper_url, dataset_url, hf_dataset_id, **kwargs)
        self.static_data_path = kwargs.get("static_data_path")
        self.data = None
        self.hf_dataset_id = hf_dataset_id
        self.paper_url = paper_url
        self.dataset_url = dataset_url

    def download(self):
        with open(self.static_data_path, "r") as f:
            all_datasets = json.load(f)
        return all_datasets

    def refresh(self) -> None:
        pass

    def process(self, data: Dict[str, Any]):
        paper_url = self.paper_url
        dataset_url = self.dataset_url
        language = data.get("language_from_tags")

        if language is None:
            language = "en"
        is_public = True
        modality = data.get("modality_from_tags")
        if modality is None:
            modality = "text"

        task_categories = data.get("task_categories")
        if task_categories is None:
            task_categories = ["question-answering", "text-generation"]
        data_created = data.get("createdAt")
        if data_created is None:
            data_created = datetime.now().strftime("%Y-%m-%d")
        configs = ["gpqa_extended", "gpqa_main", "gpqa_diamond", "gpqa_experts"]

        total_len = 0
        for config in configs:
            try:
                dataset_info = get_dataset_config_info(self.hf_dataset_id, config_name=config)
                # If there's only 1 split, use that regardless of name
                if len(dataset_info.splits) == 1:
                    split_name = list(dataset_info.splits.keys())[0]
                    total_len += dataset_info.splits[split_name].num_examples
                else:
                    # Only count test or validation splits (prioritize test > validation/valid)
                    if "test" in dataset_info.splits:
                        total_len += dataset_info.splits["test"].num_examples
                    elif "validation" in dataset_info.splits:
                        total_len += dataset_info.splits["validation"].num_examples
                    elif "valid" in dataset_info.splits:
                        total_len += dataset_info.splits["valid"].num_examples
                    # If only train exists, add 0 (skip it)
            except Exception as e:
                print(f"Warning: Could not get dataset info for {config}: {e}")
        leaderboard_detail = "HF Open LLM v2"

        final_df = pd.DataFrame(
            {
                "paper_url": [paper_url],
                "dataset_url": [dataset_url],
                "language": [language],
                "is_public": [is_public],
                "modality": [modality],
                "data_created": [data_created],
                "leaderboard_detail": [leaderboard_detail],
                "total_samples": [total_len],
                "task_categories": [task_categories],
            }
        )
        self._data = final_df
        return final_df

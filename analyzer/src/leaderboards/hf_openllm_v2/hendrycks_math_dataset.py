from analyzer.src.metrics.base import Dataset
from typing import Optional, Any, Dict
import json
from datasets import get_dataset_config_info
import pandas as pd


class HendrycksMathDataset(Dataset):
    def __init__(
        self, name: str, paper_url: str, dataset_url: str, hf_dataset_id: str, **kwargs
    ):
        super().__init__(name, paper_url, dataset_url, hf_dataset_id, **kwargs)
        self.static_data_path = kwargs.get("static_data_path")
        self.data = None
        self.hf_dataset_id = hf_dataset_id
        self.paper_url = paper_url
        self.dataset_url = dataset_url

    def refresh(self) -> None:
        pass

    def download(self):
        with open(self.static_data_path, "r") as f:
            all_datasets = json.load(f)
        return all_datasets

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
        data_created = data.get("createdAt")
        configs = [
            "algebra",
            "counting_and_probability",
            "geometry",
            "intermediate_algebra",
            "number_theory",
            "prealgebra",
            "precalculus",
        ]
        data_len = 0
        for config in configs:
            try:
                dataset_info = get_dataset_config_info(self.hf_dataset_id, config_name=config)
                for split_name, split_info in dataset_info.splits.items():
                    data_len += split_info.num_examples
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
                "total_samples": [data_len],
                "task_categories": [task_categories],
            }
        )
        self._data = final_df
        return final_df

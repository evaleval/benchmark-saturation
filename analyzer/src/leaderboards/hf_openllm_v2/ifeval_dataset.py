from analyzer.src.metrics.base import Dataset
import json
from datasets import get_dataset_config_info
import pandas as pd


class IFEvalDataset(Dataset):
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

    def process(self, data):
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
        
        # Get dataset info without downloading
        try:
            dataset_info = get_dataset_config_info(self.hf_dataset_id)
            data_len = 0
            for split_name, split_info in dataset_info.splits.items():
                data_len += split_info.num_examples
        except Exception as e:
            print(f"Warning: Could not get dataset info for {self.hf_dataset_id}: {e}")
            data_len = 0
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

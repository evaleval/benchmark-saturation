from analyzer.src.metrics.base import Dataset
from typing import Optional, Any, Dict
import json
from datasets import load_dataset
import pandas as pd
import json


class HendrycksMathDataset(Dataset):
    def __init__(self, name: str, paper_url: str, dataset_url: str, hf_dataset_id: str, **kwargs):
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
    
    def process(self, data: Dict[str, Any]):
        paper_url = self.paper_url
        dataset_url = self.dataset_url
        language = data.get("language")
        if language is None:
            language = "en"
        is_public = True
        modality = data.get("modality")
        if modality is None:
            modality = "text"
        data_created = data.get("createdAt")
        data_len = load_dataset(self.hf_dataset_id, split="train")
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
            }
        )
        return final_df
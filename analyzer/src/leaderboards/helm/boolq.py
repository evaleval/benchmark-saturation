from analyzer.src.metrics.base import Dataset
from typing import Optional, Any, Dict
import json
import pandas as pd
from datasets import get_dataset_config_info


class BoolQDataset(Dataset):
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
        
        language = data.get("language_from_tags", "en")
        is_public = True
        modality = data.get("modality_from_tags", "text")
        data_created = data.get("createdAt")
        task_categories = data.get("task_categories", [])
        
        # Extract dynamic metric fields
        downloads = data.get("downloads", 0)
        likes = data.get("likes", 0)
        last_modified = data.get("last_modified", "")
        trending_score = data.get("trending_score", 0.0)
        
        # Get dataset info without downloading
        try:
            dataset_info = get_dataset_config_info(self.hf_dataset_id)
            
            # Get split sizes from metadata
            total_len = 0
            for split_name, split_info in dataset_info.splits.items():
                total_len += split_info.num_examples
        except Exception as e:
            print(f"Warning: Could not get dataset info for {self.hf_dataset_id}: {e}")
            total_len = data.get("total_samples", 0)
        
        leaderboard_detail = "HELM Classic"
        
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
                # Dynamic metrics fields
                "downloads": [downloads],
                "likes": [likes],
                "last_modified": [last_modified],
                "trending_score": [trending_score],
            }
        )
        
        self._data = final_df
        return final_df


from typing import Any, Optional
import pandas as pd
from datasets import load_dataset
from analyzer.src.metrics.base import Benchmark

class MMLUPro(Benchmark):
    def __init__(self, dataset_name: str, paper_url: str, dataset_url: str, ds_id: str):
        super().__init__(dataset_name, paper_url, dataset_url, ds_id)
        self.ds_source = load_dataset('librarian-bots/dataset_cards_with_metadata')['train']
    
    def refresh(self) -> None:
        self._data = self.ds_source.filter(lambda x: x['datasetId'] == self.ds_id, num_proc=16)
    
    def process(self, data: Any) -> pd.DataFrame:
        data = data[0]
        created_at = data['createdAt']
        # Extract clean date from ISO format string
        clean_date = created_at.split('T')[0]  # Gets '2025-04-06'
        hf_downloads = data['downloads']
        hf_likes = data['likes']
        task_categories = data['task_categories']

        return pd.DataFrame({
            'created_at': [clean_date],
            'hf_downloads': [hf_downloads],
            'hf_likes': [hf_likes],
            'task_categories': [task_categories]
        })



        
        

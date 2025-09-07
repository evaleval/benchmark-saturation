from analyzer.src.metrics.base import Dataset
from typing import Optional, Any, Dict
import json
from datasets import load_dataset
import pandas as pd


class BigBenchHard(Dataset):
    def __init__(
        self,
        name: str,
        paper_url: Optional[str] = None,
        dataset_url: Optional[str] = None,
        hf_dataset_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name, paper_url, dataset_url, hf_dataset_id, **kwargs)
        self.static_data_path = kwargs.get("static_data_path")
        self.data = None
        self.hf_dataset_id = hf_dataset_id
        self.paper_url = paper_url
        self.dataset_url = dataset_url

    def refresh(self) -> None:
        pass

    def download(self) -> Any:
        with open(self.static_data_path, "r") as f:
            all_datasets = json.load(f)
        return all_datasets

    def process(self, data: Dict[str, Any]):
        """
        Process downloaded data into a pandas DataFrame.
        """
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

        dataset_configs = [
            "boolean_expressions",
            "causal_judgement",
            "date_understanding",
            "disambiguation_qa",
            "dyck_languages",
            "formal_fallacies",
            "geometric_shapes",
            "hyperbaton",
            "logical_deduction_five_objects",
            "logical_deduction_seven_objects",
            "logical_deduction_three_objects",
            "movie_recommendation",
            "multistep_arithmetic_two",
            "navigate",
            "object_counting",
            "penguins_in_a_table",
            "reasoning_about_colored_objects",
            "ruin_names",
            "salient_translation_error_detection",
            "snarks",
            "sports_understanding",
            "temporal_sequences",
            "tracking_shuffled_objects_five_objects",
            "tracking_shuffled_objects_seven_objects",
            "tracking_shuffled_objects_three_objects",
            "web_of_lies",
            "word_sorting",
        ]

        total_len = 0

        for config in dataset_configs:
            print(f"Loading dataset {config}")
            dataset = load_dataset(self.hf_dataset_id, config, split="train")
            total_len += len(dataset)

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
            }
        )
        print(final_df)
        # Set the processed data
        self._data = final_df

        return final_df

from analyzer.src.metrics.base import Leaderboard
import pandas as pd


class HELMLeaderboard(Leaderboard):
    """
    HELM (Holistic Evaluation of Language Models) Leaderboard
    
    Contains datasets from HELM Lite, HELM Capabilities, and HELM Finance benchmarks.
    """
    def __init__(self, name: str, description: str = "", **kwargs):
        super().__init__(name, description, **kwargs)

    def refresh(self) -> None:
        """
        Refresh the leaderboard's own data (e.g., rankings, metadata).
        This is separate from refreshing individual datasets.
        """
        pass

    def compute_rankings(self) -> pd.DataFrame:
        """
        Compute rankings across all datasets.

        Returns:
            pd.DataFrame: Rankings data
        """
        # Placeholder implementation - can be extended with actual ranking logic
        rankings_data = []
        
        for dataset_name, dataset in self._datasets.items():
            if dataset.data is not None:
                row = {
                    "dataset_name": dataset_name,
                    "total_samples": dataset.data.iloc[0].get("total_samples", 0),
                    "leaderboard_detail": dataset.data.iloc[0].get("leaderboard_detail", ""),
                }
                rankings_data.append(row)
        
        return pd.DataFrame(rankings_data)

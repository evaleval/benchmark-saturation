from analyzer.src.metrics.base import Leaderboard


class HFOpenLLMVB2Leaderboard(Leaderboard):
    def __init__(self, name: str, description: str = "", **kwargs):
        super().__init__(name, description, **kwargs)

    def refresh(self):
        pass

    def compute_rankings(self):
        pass

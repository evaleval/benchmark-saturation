from analyzer.src.metrics.dynamic.base import UpdatableMetric
import os
from analyzer.src.metrics.base import Dataset, Leaderboard
from typing import Dict, Optional
import requests
from dotenv import load_dotenv

import time
from urllib.parse import urlparse

load_dotenv()

class CitationMetric(UpdatableMetric):
    """
    Metric to fetch total citation count for datasets using Semantic Scholar API.
    """

    def __init__(
        self,
        name: str,
        description: str = "Total citation count from Semantic Scholar",
        api_key: Optional[str] = None,
    ):
        super().__init__(name, description)
        self.api_key =  os.getenv("SEMANTIC_SCHOLAR_API_KEY") if api_key is None else api_key
        # print(f"Using Semantic Scholar API Key: {'Provided' if self.api_key else 'Not Provided'}")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self._cache = {}

    def _extract_paper_id(self, paper_url: str) -> Optional[str]:
        """Extract paper ID from Semantic Scholar URL."""
        try:
            # URL format: https://www.semanticscholar.org/paper/{title}/{paperId}
            path = urlparse(paper_url).path
            parts = path.split('/')
            if len(parts) >= 3 and parts[1] == 'paper':
                return parts[-1]  # Last part is the paper ID
        except Exception as e:
            print(f"Error extracting paper ID from {paper_url}: {e}")
        return None

    def _fetch_citation_count(self, paper_id: str) -> Optional[int]:
        """
        Fetch citation count from Semantic Scholar API.
        
        Args:
            paper_id: Semantic Scholar paper ID
            
        Returns:
            Total citation count or None if error
        """
        if paper_id in self._cache:
            return self._cache[paper_id]

        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key

        # Only request citationCount field
        query_params = {"fields": "title,year,abstract,citationCount"}
        url = f"{self.base_url}/paper/{paper_id}"

        try:
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            data = response.json()

            citation_count = data.get("citationCount", 0)
            self._cache[paper_id] = citation_count
            
            # Rate limiting: be nice to the API
            time.sleep(0.1)
            
            return citation_count

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for paper {paper_id}: {e}")
            return None

    def _compute(self, dataset: Dataset) -> Optional[int]:
        """
        Compute citation count for a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            Total citation count
        """
        if not hasattr(dataset, 'paper_url') or not dataset.paper_url:
            print(f"No paper URL available for dataset {dataset.name}")
            return None

        paper_id = self._extract_paper_id(dataset.paper_url)
        if not paper_id:
            print(f"Could not extract paper ID from URL for dataset {dataset.name}")
            return None

        return self._fetch_citation_count(paper_id)

    def run_on_dataset(self, dataset: Dataset) -> Optional[int]:
        """
        Run the metric on a single dataset.

        Args:
            dataset: The dataset to analyze

        Returns:
            Citation count for the dataset's paper
        """
        return self._compute(dataset)

    def run_on_leaderboard(self, leaderboard: Leaderboard) -> Dict[str, Optional[int]]:
        """
        Run the metric on all datasets in a leaderboard.

        Args:
            leaderboard: The leaderboard to analyze

        Returns:
            Dict mapping dataset names to their citation counts
        """
        datasets = leaderboard.datasets
        leaderboard_results = {}

        for dataset_name, dataset in datasets.items():
            print(f"Fetching citations for {dataset_name}...")
            citation_count = self._compute(dataset)
            leaderboard_results[dataset_name] = citation_count

        return leaderboard_results

    def _compute_current(self, leaderboard: Leaderboard) -> Dict[str, Optional[int]]:
        """
        Compute current citation counts (for UpdatableMetric interface).
        """
        return self.run_on_leaderboard(leaderboard)
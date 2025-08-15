"""
CSV Processor Example

This module demonstrates how to use the metrics architecture to:
1. Read a CSV file containing benchmark information
2. Apply various metrics to each benchmark
3. Output an enhanced CSV with the computed metrics
"""

import pandas as pd
from typing import List, Dict, Any
from analyzer.src.metrics.base import Benchmark
from analyzer.src.metrics.static.base import StaticMetric
from analyzer.src.metrics.dynamic.base import UpdatableMetric
from analyzer.src.metrics.examples import (
    ExampleBenchmark, 
    NumSamplesMetric, 
    AvgTextLengthMetric, 
    NumClassesMetric,
    CitationCountMetric,
    DownloadCountMetric
)


class CSVBenchmarkProcessor:
    """
    A processor that reads benchmark data from CSV and applies metrics.
    """
    
    def __init__(self, static_metrics: List[StaticMetric] = None, 
                 dynamic_metrics: List[UpdatableMetric] = None):
        self.static_metrics = static_metrics or []
        self.dynamic_metrics = dynamic_metrics or []
        self.all_metrics = self.static_metrics + self.dynamic_metrics
    
    def create_benchmark_from_row(self, row: Dict[str, Any]) -> Benchmark:
        """
        Create a benchmark instance from a CSV row.
        
        Args:
            row: Dictionary representing a CSV row
            
        Returns:
            Benchmark: A benchmark instance
        """
        # Create sample data based on the benchmark info
        # In a real implementation, you might download actual data
        sample_data = pd.DataFrame({
            'text': [f"Sample text for {row.get('name', 'benchmark')}"],
            'label': [0],
            'length': [len(row.get('name', 'benchmark'))]
        })
        
        return ExampleBenchmark(
            name=row.get('name', 'unknown'),
            paper_url=row.get('paper_url'),
            dataset_url=row.get('dataset_url'),
            initial_data=sample_data
        )
    
    def process_csv(self, input_file: str, output_file: str) -> pd.DataFrame:
        """
        Process a CSV file and output an enhanced version with metrics.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
            
        Returns:
            pd.DataFrame: The processed data with metrics
        """
        # Read the input CSV
        df = pd.read_csv(input_file)
        results = []
        
        print(f"Processing {len(df)} benchmarks...")
        
        for idx, row in df.iterrows():
            print(f"Processing benchmark {idx + 1}/{len(df)}: {row.get('name', 'unknown')}")
            
            # Create benchmark from row
            benchmark = self.create_benchmark_from_row(row.to_dict())
            
            # Initialize result row with original data
            result_row = row.to_dict()
            
            # Apply static metrics
            for metric in self.static_metrics:
                try:
                    score = metric.run(benchmark)
                    result_row[f"static_{metric.name}"] = score
                except Exception as e:
                    print(f"Error computing {metric.name}: {e}")
                    result_row[f"static_{metric.name}"] = None
            
            # Apply dynamic metrics
            for metric in self.dynamic_metrics:
                try:
                    score = metric.run(benchmark)
                    result_row[f"dynamic_{metric.name}"] = score
                    
                    # Add historical info
                    historical = metric.get_historical_values(benchmark)
                    result_row[f"dynamic_{metric.name}_history_count"] = len(historical)
                except Exception as e:
                    print(f"Error computing {metric.name}: {e}")
                    result_row[f"dynamic_{metric.name}"] = None
                    result_row[f"dynamic_{metric.name}_history_count"] = 0
            
            results.append(result_row)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        
        # Save to CSV
        output_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        return output_df


def create_sample_input_csv(filename: str = "sample_benchmarks.csv"):
    """
    Create a sample input CSV file for testing.
    
    Args:
        filename: Output filename
    """
    sample_data = [
        {
            'name': 'GLUE-MNLI',
            'paper_url': 'https://arxiv.org/abs/1804.07461',
            'dataset_url': 'https://huggingface.co/datasets/glue',
            'description': 'Multi-Genre Natural Language Inference'
        },
        {
            'name': 'SQuAD-v2',
            'paper_url': 'https://arxiv.org/abs/1806.03822',
            'dataset_url': 'https://huggingface.co/datasets/squad_v2',
            'description': 'Stanford Question Answering Dataset'
        },
        {
            'name': 'CoLA',
            'paper_url': 'https://arxiv.org/abs/1805.12471',
            'dataset_url': 'https://huggingface.co/datasets/glue',
            'description': 'Corpus of Linguistic Acceptability'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(filename, index=False)
    print(f"Created sample input CSV: {filename}")
    return filename


def run_csv_processor_example():
    """
    Run a complete example of CSV processing with metrics.
    """
    print("=== CSV Processor Example ===\n")
    
    # Create sample input CSV
    input_file = create_sample_input_csv()
    
    # Create metrics
    static_metrics = [
        NumSamplesMetric(),
        AvgTextLengthMetric(),
        NumClassesMetric()
    ]
    
    dynamic_metrics = [
        CitationCountMetric(),
        DownloadCountMetric()
    ]
    
    # Create processor
    processor = CSVBenchmarkProcessor(static_metrics, dynamic_metrics)
    
    # Process the CSV
    output_file = "enhanced_benchmarks.csv"
    result_df = processor.process_csv(input_file, output_file)
    
    print("\n=== Results Summary ===")
    print(f"Input benchmarks: {len(result_df)}")
    print(f"Static metrics applied: {len(static_metrics)}")
    print(f"Dynamic metrics applied: {len(dynamic_metrics)}")
    
    # Show the enhanced CSV structure
    print(f"\nEnhanced CSV columns: {list(result_df.columns)}")
    
    # Show a sample row
    print(f"\nSample processed row:")
    sample_row = result_df.iloc[0]
    for col in result_df.columns:
        print(f"  {col}: {sample_row[col]}")
    
    return result_df


if __name__ == "__main__":
    run_csv_processor_example() 
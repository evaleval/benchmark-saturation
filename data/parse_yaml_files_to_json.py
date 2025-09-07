import yaml
import json
import os
from pathlib import Path


def parse_yaml_files_to_json():
    """
    Parse all YAML files from the split_yaml folder and convert them to JSON format
    where datasetId is the key and the rest of the fields are the values.
    """

    # Define paths
    split_yaml_dir = Path("/Users/random/benchmark-saturation/data/split_yaml")
    output_file = "all_datasets.json"

    # Dictionary to store all datasets with datasetId as key
    all_datasets = {}

    # Get all YAML files in the split_yaml directory
    yaml_files = sorted(split_yaml_dir.glob("all_dataset_info_part*.yaml"))

    print(f"Found {len(yaml_files)} YAML files to process:")
    for file in yaml_files:
        print(f"  - {file.name}")

    # Process each YAML file
    for yaml_file in yaml_files:
        print(f"\nProcessing {yaml_file.name}...")

        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                # Read the file content
                content = f.read()

                # Split content by datasetId entries
                # Each dataset starts with "datasetId:"
                datasets = []
                current_dataset = {}

                lines = content.split("\n")
                for line in lines:
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Check if this line starts a new dataset
                    if line.startswith("datasetId:"):
                        # Save previous dataset if it exists
                        if current_dataset and "datasetId" in current_dataset:
                            datasets.append(current_dataset)

                        # Start new dataset
                        current_dataset = {}
                        current_dataset["datasetId"] = line.split(":", 1)[1].strip()

                    # Add other fields to current dataset
                    elif ":" in line and current_dataset:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()

                        # Handle different value types
                        if value == "[]":
                            current_dataset[key] = []
                        elif value == "null" or value == "":
                            current_dataset[key] = None
                        elif value.startswith("'") and value.endswith("'"):
                            current_dataset[key] = value[1:-1]  # Remove quotes
                        elif value.startswith('"') and value.endswith('"'):
                            current_dataset[key] = value[1:-1]  # Remove quotes
                        elif value.lower() in ["true", "false"]:
                            current_dataset[key] = value.lower() == "true"
                        elif value.replace(".", "").replace("-", "").isdigit():
                            # Try to convert to number
                            try:
                                if "." in value:
                                    current_dataset[key] = float(value)
                                else:
                                    current_dataset[key] = int(value)
                            except ValueError:
                                current_dataset[key] = value
                        else:
                            current_dataset[key] = value

                # Don't forget the last dataset
                if current_dataset and "datasetId" in current_dataset:
                    datasets.append(current_dataset)

                print(f"  Found {len(datasets)} datasets in {yaml_file.name}")

                # Add datasets to the main dictionary
                for dataset in datasets:
                    dataset_id = dataset["datasetId"]
                    if dataset_id in all_datasets:
                        print(f"  Warning: Duplicate datasetId found: {dataset_id}")
                    all_datasets[dataset_id] = dataset

        except Exception as e:
            print(f"  Error processing {yaml_file.name}: {str(e)}")
            continue

    # Save to JSON file
    print(f"\nSaving {len(all_datasets)} datasets to {output_file}...")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_datasets, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved {len(all_datasets)} datasets to {output_file}")

        # Print some statistics
        print(f"\nStatistics:")
        print(f"  Total datasets: {len(all_datasets)}")

        # Show a sample dataset
        if all_datasets:
            sample_id = list(all_datasets.keys())[0]
            sample_dataset = all_datasets[sample_id]
            print(f"\nSample dataset ({sample_id}):")
            for key, value in sample_dataset.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error saving to JSON file: {str(e)}")


if __name__ == "__main__":
    parse_yaml_files_to_json()

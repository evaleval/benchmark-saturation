import yaml
import json
import os
from pathlib import Path
import re


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
                content = f.read()

            # Split content by dataset entries (each starts with "datasetId:" at beginning of line)
            dataset_blocks = []
            current_block = []

            lines = content.split("\n")
            for line in lines:
                # Check if this line starts a new dataset (datasetId at start of line, not indented)
                if re.match(r"^datasetId:\s+", line) and current_block:
                    # Save previous dataset block, removing empty lines at start/end
                    block_content = "\n".join(current_block).strip()
                    if block_content:
                        dataset_blocks.append(block_content)
                    current_block = [line]
                else:
                    current_block.append(line)

            # Don't forget the last block
            if current_block:
                block_content = "\n".join(current_block).strip()
                if block_content:
                    dataset_blocks.append(block_content)

            print(f"  Found {len(dataset_blocks)} dataset blocks in {yaml_file.name}")

            # Parse each dataset block as YAML
            for i, block in enumerate(dataset_blocks):
                try:
                    # Clean the block - remove any document separators or invalid characters
                    cleaned_block = block.strip()

                    if not cleaned_block:
                        continue

                    # Try manual parsing first for better control
                    try:
                        dataset = parse_dataset_manually(cleaned_block)
                        if not dataset or "datasetId" not in dataset:
                            # Fall back to YAML parsing if manual parsing fails
                            dataset = yaml.safe_load(cleaned_block)
                    except Exception:
                        # If manual parsing fails, try YAML parsing
                        try:
                            dataset = yaml.safe_load(cleaned_block)
                        except yaml.scanner.ScannerError:
                            # If YAML parsing also fails due to document separators, try FullLoader
                            try:
                                dataset = yaml.load(
                                    cleaned_block, Loader=yaml.FullLoader
                                )
                            except:
                                print(f"  Skipping block {i+1}: Unable to parse")
                                continue

                    if dataset and isinstance(dataset, dict) and "datasetId" in dataset:
                        dataset_id = dataset["datasetId"]

                        # Parse tags into separate key-value pairs
                        if "tags" in dataset and isinstance(dataset["tags"], list):
                            parsed_tags = parse_tags_to_fields(dataset["tags"])

                            # Add parsed tag fields to the dataset
                            for key, value in parsed_tags.items():
                                # Only add if the field doesn't already exist or is None
                                if key not in dataset or dataset[key] is None:
                                    dataset[key] = value

                            # Keep only non-metadata tags in the tags field
                            remaining_tags = parsed_tags.get("remaining_tags", [])
                            dataset["tags"] = remaining_tags if remaining_tags else None

                        if dataset_id in all_datasets:
                            print(f"  Warning: Duplicate datasetId found: {dataset_id}")

                        all_datasets[dataset_id] = dataset

                except Exception as e:
                    print(f"  Error processing block {i+1}: {str(e)}")
                    continue

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

        # Show datasets with task_categories to verify the fix
        datasets_with_task_categories = {
            k: v
            for k, v in all_datasets.items()
            if v.get("task_categories") is not None
        }
        print(f"  Datasets with task_categories: {len(datasets_with_task_categories)}")

        # Show statistics for parsed tag fields
        tag_fields = [
            "language_from_tags",
            "license_from_tags",
            "size_categories_from_tags",
            "format_from_tags",
            "modality_from_tags",
            "library_from_tags",
            "region_from_tags",
        ]

        for field in tag_fields:
            count = sum(1 for d in all_datasets.values() if d.get(field) is not None)
            print(f"  Datasets with {field}: {count}")

        # Show a sample dataset with task_categories
        if datasets_with_task_categories:
            sample_id = list(datasets_with_task_categories.keys())[0]
            sample_dataset = datasets_with_task_categories[sample_id]
            print(f"\nSample dataset with task_categories ({sample_id}):")
            print(f"  task_categories: {sample_dataset.get('task_categories')}")
            print(f"  language_from_tags: {sample_dataset.get('language_from_tags')}")
            print(f"  license_from_tags: {sample_dataset.get('license_from_tags')}")

    except Exception as e:
        print(f"Error saving to JSON file: {str(e)}")


def parse_tags_to_fields(tags):
    """
    Parse tags list into separate fields based on prefixes.
    Returns a dictionary with parsed fields and remaining tags.
    """
    parsed = {
        "task_categories_from_tags": [],
        "language_from_tags": [],
        "license_from_tags": [],
        "size_categories_from_tags": [],
        "format_from_tags": [],
        "modality_from_tags": [],
        "library_from_tags": [],
        "region_from_tags": [],
        "remaining_tags": [],
    }

    for tag in tags:
        if not isinstance(tag, str):
            parsed["remaining_tags"].append(tag)
            continue

        if tag.startswith("task_categories:"):
            parsed["task_categories_from_tags"].append(
                tag[16:]
            )  # Remove 'task_categories:' prefix
        elif tag.startswith("language:"):
            parsed["language_from_tags"].append(tag[9:])  # Remove 'language:' prefix
        elif tag.startswith("license:"):
            parsed["license_from_tags"].append(tag[8:])  # Remove 'license:' prefix
        elif tag.startswith("size_categories:"):
            parsed["size_categories_from_tags"].append(
                tag[16:]
            )  # Remove 'size_categories:' prefix
        elif tag.startswith("format:"):
            parsed["format_from_tags"].append(tag[7:])  # Remove 'format:' prefix
        elif tag.startswith("modality:"):
            parsed["modality_from_tags"].append(tag[9:])  # Remove 'modality:' prefix
        elif tag.startswith("library:"):
            parsed["library_from_tags"].append(tag[8:])  # Remove 'library:' prefix
        elif tag.startswith("region:"):
            parsed["region_from_tags"].append(tag[7:])  # Remove 'region:' prefix
        else:
            # This is a regular tag, not metadata
            parsed["remaining_tags"].append(tag)

    # Convert single-item lists to strings, empty lists to None
    for key in parsed:
        if key == "remaining_tags":
            continue
        if len(parsed[key]) == 0:
            parsed[key] = None
        elif len(parsed[key]) == 1:
            parsed[key] = parsed[key][0]
        # Keep as list if multiple values

    return parsed


def parse_dataset_manually(block):
    """
    Manual parser for datasets that fail YAML parsing due to embedded content.
    """
    dataset = {}
    lines = block.split("\n")
    current_key = None
    current_value = []
    in_list = False
    in_multiline_string = False
    string_quote_char = None
    indent_level = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Calculate indentation level
        line_indent = len(line) - len(line.lstrip())

        # Check if this is a new key-value pair (not indented, contains colon, not in multiline string)
        if (
            ":" in line
            and line_indent == 0
            and not line.startswith("-")
            and not in_multiline_string
        ):
            # Save previous key if exists
            if current_key:
                if in_list:
                    dataset[current_key] = current_value
                else:
                    value_str = (
                        "\n".join(current_value).strip() if current_value else None
                    )
                    dataset[current_key] = value_str

            # Parse new key
            if ":" in line:
                key, value = line.split(":", 1)
                current_key = key.strip()
                value = value.strip()

                # Check if this starts a multiline string
                if value.startswith("'"):
                    string_quote_char = "'"
                    # Handle multiline strings that might contain --- or other YAML content
                    if value.count("'") >= 2:
                        # Complete single-line quoted string
                        dataset[current_key] = value.strip("'")
                        current_key = None
                        in_multiline_string = False
                    else:
                        # Start of multiline string - collect everything until closing quote
                        current_value = [value[1:]]  # Remove opening quote
                        in_multiline_string = True
                        in_list = False

                        # Look ahead to find the closing quote
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j]
                            current_value.append(next_line)
                            if next_line.rstrip().endswith("'"):
                                # Found closing quote
                                full_value = "\n".join(current_value)
                                # Remove the trailing quote
                                if full_value.endswith("'"):
                                    full_value = full_value[:-1]
                                dataset[current_key] = full_value
                                current_key = None
                                in_multiline_string = False
                                i = j  # Skip to after the closing quote
                                break
                            j += 1
                        else:
                            # Didn't find closing quote, treat as regular multiline
                            dataset[current_key] = "\n".join(current_value)
                            current_key = None
                            in_multiline_string = False

                elif not value:
                    # This might be a list or multiline value
                    current_value = []
                    in_list = False
                    in_multiline_string = False
                else:
                    # Simple value
                    dataset[current_key] = parse_simple_value(value)
                    current_key = None

        elif line.startswith("- ") and current_key and line_indent == 0:
            # Top-level list item
            if not in_list:
                current_value = []
                in_list = True
            current_value.append(line[2:].strip())

        elif current_key and line_indent > 0 and not in_multiline_string:
            # Continuation of previous value (indented)
            current_value.append(stripped)

        i += 1

    # Don't forget the last key
    if current_key:
        if in_list:
            dataset[current_key] = current_value
        else:
            value_str = "\n".join(current_value).strip() if current_value else None
            dataset[current_key] = value_str

    return dataset


def parse_simple_value(value):
    """Parse a simple YAML value and convert to appropriate Python type."""
    value = value.strip()

    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    elif value.lower() == "null":
        return None
    elif value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    elif value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    elif value.isdigit():
        return int(value)
    elif re.match(r"^\d+\.\d+$", value):
        return float(value)
    else:
        return value


if __name__ == "__main__":
    parse_yaml_files_to_json()

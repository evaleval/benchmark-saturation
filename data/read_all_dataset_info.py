"""
read_all_dataset_info.py
-----------------------

This script allows you to interactively view YAML data from split files generated from the HuggingFace dataset export.

Features:
- Print all fields or only the parsed 'card' field for the first N rows of a split YAML file.
- Accepts either a split number (e.g., 1 for part1) or a direct YAML file path.
- Interactive prompts for number of rows and data type to display.

Usage:
    python read_all_dataset_info.py <split_number|yaml_file>

Examples:
    python read_all_dataset_info.py 1
    python read_all_dataset_info.py split_yaml/all_dataset_info_part2.yaml
"""

import sys
import yaml

def print_first_n_yaml_docs(filepath, n=5):
    with open(filepath, "r") as f:
        for i, doc in enumerate(yaml.safe_load_all(f)):
            if i >= n:
                break
            print(f"--- Document {i+1} (ALL DATA) ---")
            print(yaml.dump(doc, sort_keys=False, indent=2, allow_unicode=True))
            print()

def print_first_n_card_parsed(filepath, n=5):
    """
    Print only the 'card_parsed' field from the first n documents in a YAML file.
    Args:
        filepath (str): Path to the YAML file.
        n (int): Number of documents to print.
    Returns: None
    """
    with open(filepath, "r") as f:
        for i, doc in enumerate(yaml.safe_load_all(f)):
            if i >= n:
                break
            print(f"--- Document {i+1} (card_parsed) ---")
            card_parsed = doc.get("card_parsed", None)
            if card_parsed is not None:
                print(yaml.dump(card_parsed, sort_keys=False, indent=2, allow_unicode=True))
            else:
                print("No card_parsed data found.")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_all_dataset_info.py <split_number|yaml_file>")
        print("  Example: python read_all_dataset_info.py 1   # interactively choose what to print from part 1")
        print("  Example: python read_all_dataset_info.py split_yaml/all_dataset_info_part2.yaml")
    else:
        arg = sys.argv[1]
        if arg.isdigit():
            split_num = int(arg)
            yaml_file = f"split_yaml/all_dataset_info_part{split_num}.yaml"
        else:
            yaml_file = arg

        # Interactive prompt
        while True:
            try:
                n = int(input("How many rows do you want to see? (default 1): ") or "1")
                break
            except ValueError:
                print("Please enter a valid integer.")
        while True:
            choice = input("Show (a)ll data or only (c)ards? [a/c, default a]: ").strip().lower() or "a"
            if choice in ("a", "c"):
                break
            print("Please enter 'a' or 'c'.")
        if choice == "a":
            print_first_n_yaml_docs(yaml_file, n)
        else:
            print_first_n_card_parsed(yaml_file, n)

def main():
    """
    Main interactive entry point for the script.
    Prompts user for number of rows and data type to display.
    """
    if len(sys.argv) < 2:
        print("Usage: python read_all_dataset_info.py <split_number|yaml_file>")
        print("  Example: python read_all_dataset_info.py 1   # interactively choose what to print from part 1")
        print("  Example: python read_all_dataset_info.py split_yaml/all_dataset_info_part2.yaml")
        return
    arg = sys.argv[1]
    if arg.isdigit():
        split_num = int(arg)
        yaml_file = f"split_yaml/all_dataset_info_part{split_num}.yaml"
    else:
        yaml_file = arg

    # Interactive prompt
    while True:
        try:
            n = int(input("How many rows do you want to see? (default 1): ") or "1")
            break
        except ValueError:
            print("Please enter a valid integer.")
    while True:
        choice = input("Show (a)ll data or only (c)ards? [a/c, default a]: ").strip().lower() or "a"
        if choice in ("a", "c"):
            break
        print("Please enter 'a' or 'c'.")
    if choice == "a":
        print_first_n_yaml_docs(yaml_file, n)
    else:
        print_first_n_card_parsed(yaml_file, n)

if __name__ == "__main__":
    main()
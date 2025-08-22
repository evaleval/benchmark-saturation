
import os
import yaml
from datasets import load_dataset
from tqdm import tqdm

# Parameters
ENTRIES_PER_FILE = 20000
OUTPUT_DIR = "data/split_yaml"
os.makedirs(OUTPUT_DIR, exist_ok=True)


ds = load_dataset("librarian-bots/dataset_cards_with_metadata")
print(f"Dataset loaded successfully with {len(ds['train'])} entries")

entries = []
for entry in tqdm(ds["train"], desc="Parsing entries"):
    entry_dict = dict(entry)
    if "card" in entry_dict and entry_dict["card"]:
        try:
            entry_dict["card_parsed"] = list(yaml.safe_load_all(entry_dict["card"]))
        except Exception as e:
            entry_dict["card_parsed"] = f"YAML parse error: {e}"
    entries.append(entry_dict)

num_files = (len(entries) + ENTRIES_PER_FILE - 1) // ENTRIES_PER_FILE
print("Saving chunks:")
for i in range(num_files):
    chunk = entries[i*ENTRIES_PER_FILE:(i+1)*ENTRIES_PER_FILE]
    out_path = os.path.join(OUTPUT_DIR, f"all_dataset_info_part{i+1}.yaml")
    with open(out_path, "w") as f:
        for doc in chunk:
            yaml.dump(doc, f, sort_keys=False, indent=2)
            f.write('---\n')
    print(".", end="", flush=True)
print(f"\nDone! {num_files} files created in {OUTPUT_DIR}")

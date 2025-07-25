
import json
import numpy as np
import umap
from sklearn.preprocessing import MinMaxScaler

# Read data from the saturation JSON file 
with open("website/web/data/saturation.json", "r") as f:
    data_saturation = json.load(f)

# Vectorise data
tasks = list(data_saturation.keys())
task_to_vector = {task: [1 if i == j else 0 for i in range(len(tasks))] for j, task in enumerate(tasks)}

vectorized_data = []
for task, datasets in data_saturation.items():
    for dataset_name, data in datasets.items():
        vectorized_data.append({
            "name": dataset_name,
            "task": task,
            "saturation": data["saturation"],
            "vector": [
                *task_to_vector[task],
                data["saturation"],
                data["year"],
                1 if data["public"] else 0,
                data["size"]
            ]
        })

vectors = np.array([d["vector"] for d in vectorized_data])

# Scale the data before UMAP
scaler = MinMaxScaler()
scaled_vectors = scaler.fit_transform(vectors)

# Apply UMAP
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
embedding = reducer.fit_transform(scaled_vectors)

# Create the output data structure
output_data = []
for i, d in enumerate(vectorized_data):
    output_data.append({
        "name": d["name"],
        "task": d["task"],
        "saturation": d["saturation"],
        "x": float(embedding[i, 0]),
        "y": float(embedding[i, 1])
    })

# Save to A JSON file for the website to use
with open("website/web/data/projections.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("UMAP projections generated and saved to website/web/data/projections.json") 
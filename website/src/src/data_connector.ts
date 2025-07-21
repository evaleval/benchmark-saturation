export let DATA_SATURATION = {};

export async function fetch_data_saturation() {
    const response = await fetch('data/saturation.json');
    DATA_SATURATION = await response.json();
    return DATA_SATURATION;
}

export function getVectorizedDataSaturation(DATA_SATURATION) {
  // task to vector
  let taskToVector = {}
  Object.keys(DATA_SATURATION).forEach((task, index) => {
    // 1-hot encoded
    taskToVector[task] = Array(14).fill(0);
    taskToVector[task][index] = 1;
  });

  // [Task type (0/1 encoded), saturation, year, public (0/1), size]
  let vectorizedData = [];
  for (const [task, datasets] of Object.entries(DATA_SATURATION)) {
    for (const dataset of Object.keys(datasets)) {
      const data = datasets[dataset];
      vectorizedData.push({
        "name": dataset,
        "task": task,
        "saturation": data.saturation,
        "vector": [
          ...taskToVector[task],
          data.saturation,
          data.year,
          data.public ? 1 : 0,
          data.size
        ]
      });
    }
  }

  return vectorizedData;
}
# %%

import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("../web/figures", exist_ok=True)

plt.rcParams.update({'font.family': 'serif'})


xtickslabels = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

performance = {
    "machine_translation": {
        "average_model": [0.2, 0.2, 0.5, 0.5, 0.5, 0.6, 0.9, 1.1, 1.1],
        "best_model": [0.3, 0.3, 0.6, 0.7, 0.8, 1.0, 1.2, 1.2, 1.2],
        "best_output": [0.4, 0.4, 0.7, 0.8, 1.0, 1.2, 1.3, 1.3, 1.3],
    },
    "summarization": {
        "average_model": [0.1, 0.1, 0.15, 0.2, 0.25, 0.3, 0.9, 1.1, 1.3],
        "best_model": [0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 1.0, 1.2, 1.4],
        "best_output": [0.3, 0.3, 0.4, 0.5, 0.6, 0.8, 1.1, 1.3, 1.5],
    },
    "question_answering": {
        "average_model": [0.15, 0.15, 0.2, 0.25, 0.3, 0.4, 0.8, 0.8, 0.85],
        "best_model": [0.25, 0.25, 0.35, 0.45, 0.55, 0.7, 1.1, 1.3, 1.5],
        "best_output": [0.35, 0.35, 0.45, 0.55, 0.65, 0.8, 0.9, 0.9, 0.96],
    },
    "dialogue_generation": {
        "average_model": [0.05, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.7, 0.7],
        "best_model": [0.1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0, 1.2],
        "best_output": [0.15, 0.15, 0.25, 0.35, 0.45, 0.6, 1.1, 1.3, 1.5],
    },
}

for human_line in ["hum", "nohum"]:
    for mode in performance["machine_translation"].keys():
        plt.figure(figsize=(9, 3))

        for task in performance.keys():
            ys = performance[task][mode]
            ys += np.random.normal(0, 0.1, len(ys))
            plt.plot(
                xtickslabels,
                ys,
                label=task.replace("_", " ").title() + (r" $\bf{is\,solved}$" if ys[-1] >= 1.0 else r" $\bf{is\,not\,solved}$"),
                marker="o",
            )

        if human_line == "hum":
            plt.axhline(1.0, color="black", linestyle="--", label="Human-level")
        plt.ylabel("Performance (normalized)")
        plt.gca().patch.set_visible(False)

        plt.legend(
            loc="upper left",
            bbox_to_anchor=(1.05, 1),
            borderaxespad=0,
            fontsize=10,
            frameon=False,
        )

        plt.gca().spines[["top", "right"]].set_visible(False)
        plt.tight_layout(pad=1)
        plt.savefig(f"../web/figures/mock_performance_{mode}_{human_line}.svg", transparent=True)

# %%

performance = {
    "bleu": [0.2, 0.3, 0.4, 0.9, 0.95, 0.95, 0.96, 0.97, 0.98],
    "comet": [0.7, 0.7, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.8],
    "human_esa": [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9],
    "human_da": [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
}

plt.figure(figsize=(9, 3))
for metric, ys in performance.items():
    ys += np.random.normal(0, 0.05, len(ys))
    plt.plot(
        xtickslabels,
        ys,
        label=metric.replace("_", " ").title(),
        marker="o",
    )

plt.ylabel("Evaluation Score")
plt.gca().patch.set_visible(False)
plt.legend(
    loc="upper left",
    bbox_to_anchor=(1.05, 1),
    borderaxespad=0,
    fontsize=10,
    frameon=False,
)
plt.gca().spines[["top", "right"]].set_visible(False)
plt.tight_layout(pad=1)
plt.savefig("../web/figures/mock_metrics.svg", transparent=True)

# %%

performance = {
    "wikipedia 2017": [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1],
    "opus 2019": [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0],
    "common crawl 2020": [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9],
    "web text 2021": [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8],
}
start_i = {
    "wikipedia 2017": 0,
    "opus 2019": 1,
    "common crawl 2020": 2,
    "web text 2021": 3,
}
plt.figure(figsize=(9, 3))
for dataset, ys in performance.items():
    ys += np.random.normal(0, 0.05, len(ys))
    plt.plot(
        xtickslabels[start_i[dataset]:],
        ys[start_i[dataset]:],
        label=dataset.replace("_", " ").title(),
        marker="o",
    )
plt.ylabel("Performance (normalized)")
plt.axhline(1.0, color="black", linestyle="--", label="Human-level")
plt.gca().patch.set_visible(False)
plt.legend(
    loc="upper left",
    bbox_to_anchor=(1.05, 1),
    borderaxespad=0,
    fontsize=10,
    frameon=False,
)
plt.gca().spines[["top", "right"]].set_visible(False)
plt.tight_layout(pad=1)
plt.savefig("../web/figures/mock_datasets.svg", transparent=True)
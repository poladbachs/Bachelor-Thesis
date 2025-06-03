import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colormaps as cm

# File mapping
ablation_files = {
    "Qwen0.5B +L1 Only": "results/1_qw05_l1_metrics.csv",
    "Qwen0.5B Full": "results/5_qw05_l5_metrics.csv",
    "Qwen0.5B - L1": "additional_results/15_qw05_nol1_metrics.csv",
    "Qwen0.5B - L2": "additional_results/16_qw05_nol2_metrics.csv",
    "Qwen0.5B - L1 - L4": "additional_results/17_qw05_nol14_metrics.csv",
    "Qwen0.5B - L1 - L4 - L5": "additional_results/18_qw05_nol145_metrics.csv",

    "Qwen1.5B +L1 only": "results/6_qw15_l1_metrics.csv",
    "Qwen1.5B Full": "results/10_qw15_l5_metrics.csv",
    "Qwen1.5B - L1": "additional_results/19_qw15_nol1_metrics.csv",
    "Qwen1.5B - L1 - L4": "additional_results/20_qw15_nol14_metrics.csv",
    "Qwen1.5B - L1 - L5": "additional_results/21_qw15_nol15_metrics.csv",
    "Qwen1.5B - L1 - L3": "additional_results/22_qw15_nol13_metrics.csv",

    "DeepSeek +L1 only": "results/11_de13_l1_metrics.csv",
    "DeepSeek Full": "results/15_de13_l5_metrics.csv",
    "DeepSeek - L2": "additional_results/23_de13_nol2_metrics.csv",
    "DeepSeek - L2 - L4": "additional_results/24_de13_nol24_metrics.csv",
    "DeepSeek - L2 - L4 - L5": "additional_results/25_de13_nol245_metrics.csv",
}

# Extract accuracy values
acc_data = []
for label, path in ablation_files.items():
    df = pd.read_csv(path)
    acc_row = df[df["Metric"] == "Accuracy"]
    if not acc_row.empty:
        acc_data.append({
            "Model": label.split(" ")[0],
            "Setting": label.replace("Qwen0.5B ", "")
                            .replace("Qwen1.5B ", "")
                            .replace("DeepSeek ", ""),
            "Accuracy": float(acc_row["Value"].iloc[0])
        })

df_acc = pd.DataFrame(acc_data)

# Define colormaps
color_maps = {
    "Qwen0.5B": cm["Blues"],
    "Qwen1.5B": cm["Reds"],
    "DeepSeek": cm["Oranges"]
}

# Assign colors
final_colors = []
model_counts = df_acc["Model"].value_counts().to_dict()
model_order = {m: 0 for m in model_counts}

for _, row in df_acc.iterrows():
    m = row["Model"]
    total = model_counts[m]
    i = model_order[m]
    final_colors.append(color_maps[m](0.4 + 0.5 * (i / max(total - 1, 1))))
    model_order[m] += 1

df_acc["Color"] = final_colors

# Plot: 3 subfigures
plt.figure(figsize=(20, 6))
sns.set_style("whitegrid")

models = ["Qwen0.5B", "Qwen1.5B", "DeepSeek"]

for i, model in enumerate(models, 1):
    plt.subplot(1, 3, i)
    subset = df_acc[df_acc["Model"] == model].copy()
    subset["Setting"] = pd.Categorical(subset["Setting"], ordered=True, categories=subset["Setting"].tolist())
    ax = sns.barplot(data=subset, x="Setting", y="Accuracy", palette=list(subset["Color"]))

    plt.title(model, fontsize=18)
    plt.xlabel("Layer Removal Setting", fontsize=14)
    if i == 1:
        plt.ylabel("Accuracy", fontsize=14)
    else:
        plt.ylabel("")
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(fontsize=12)
    plt.ylim(0.3, 0.6)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for p in ax.patches:
        height = p.get_height()
        if not pd.isna(height):
            ax.annotate(f'{height:.3f}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=14, color='black', xytext=(0, 3),
                        textcoords='offset points')

plt.suptitle("Accuracy Under Layer Removal (including Baseline Summary-Only)", fontsize=20)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("plots/ablation_accuracy_subfigs.png", dpi=300)
plt.close()
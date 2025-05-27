import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.cm import get_cmap

# File mapping
ablation_files = {
    "Qwen0.5B Full": "results/5_qw05_l5_metrics.csv",
    "Qwen0.5B –L1": "additional_results/15_qw05_nol1_metrics.csv",
    "Qwen0.5B –L2": "additional_results/16_qw05_nol2_metrics.csv",
    "Qwen0.5B –L1-L4": "additional_results/17_qw05_nol14_metrics.csv",
    "Qwen0.5B –L1-L4-L5": "additional_results/18_qw05_nol145_metrics.csv",
    
    "Qwen1.5B Full": "results/10_qw15_l5_metrics.csv",
    "Qwen1.5B –L1": "additional_results/19_qw15_nol1_metrics.csv",
    "Qwen1.5B –L1-L4": "additional_results/20_qw15_nol14_metrics.csv",
    "Qwen1.5B –L1-L5": "additional_results/21_qw15_nol15_metrics.csv",
    "Qwen1.5B –L1-L3": "additional_results/22_qw15_nol13_metrics.csv",
    
    "DeepSeek Full": "results/15_de13_l5_metrics.csv",
    "DeepSeek –L2": "additional_results/23_de13_nol2_metrics.csv",
    "DeepSeek –L2-L4": "additional_results/24_de13_nol24_metrics.csv",
    "DeepSeek –L2-L4-L5": "additional_results/25_de13_nol245_metrics.csv",
}

# Extract accuracy values
acc_data = []
for label, path in ablation_files.items():
    df = pd.read_csv(path)
    acc_row = df[df["Metric"] == "Accuracy"]
    if not acc_row.empty:
        acc_data.append({
            "Model": label.split(" ")[0],
            "Setting": label,
            "Accuracy": float(acc_row["Value"].values[0])
        })

df_acc = pd.DataFrame(acc_data)

# Define custom color map per model
color_maps = {
    "Qwen0.5B": get_cmap("Blues"),
    "Qwen1.5B": get_cmap("Reds"),
    "DeepSeek": get_cmap("Oranges")
}

# Assign darkening colors per model
final_colors = []
model_counts = df_acc["Model"].value_counts().to_dict()
model_order = {model: 0 for model in model_counts}

for _, row in df_acc.iterrows():
    model = row["Model"]
    total = model_counts[model]
    i = model_order[model]
    color = color_maps[model](0.4 + 0.5 * (i / (total - 1)))  # fade from mid to dark
    final_colors.append(color)
    model_order[model] += 1

# Plot
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")

ax = sns.barplot(data=df_acc, x="Setting", y="Accuracy", palette=final_colors)
plt.title("Layer Removal Analysis: Accuracy per Model and Setting", fontsize=16)
plt.xlabel("Full Description vs Layer Removal Setting", fontsize=12)
plt.ylabel("Accuracy", fontsize=12)
plt.xticks(rotation=45, ha="right")

for p in ax.patches:
    height = p.get_height()
    ax.annotate(f'{height:.3f}', 
                (p.get_x() + p.get_width() / 2., height), 
                ha='center', va='bottom',
                fontsize=9, xytext=(0, 3), textcoords='offset points')

plt.tight_layout()
plt.savefig("plots/ablation_accuracy.png")
plt.close()

print("Saved: plots/ablation_accuracy.png")

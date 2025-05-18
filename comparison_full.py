import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Mapping all files
files = {
    "Qwen0.5B_L1": "results/1_qw05_l1_metrics.csv",
    "Qwen0.5B_L2": "results/2_qw05_l2_metrics.csv",
    "Qwen0.5B_L3": "results/3_qw05_l3_metrics.csv",
    "Qwen0.5B_L4": "results/4_qw05_l4_metrics.csv",
    "Qwen0.5B_L5": "results/5_qw05_l5_metrics.csv",

    "Qwen1.5B_L1": "results/6_qw15_l1_metrics.csv",
    "Qwen1.5B_L2": "results/7_qw15_l2_metrics.csv",
    "Qwen1.5B_L3": "results/8_qw15_l3_metrics.csv",
    "Qwen1.5B_L4": "results/9_qw15_l4_metrics.csv",
    "Qwen1.5B_L5": "results/10_qw15_l5_metrics.csv",

    "DeepSeek1.3B_L1": "results/11_de13_l1_metrics.csv",
    "DeepSeek1.3B_L2": "results/12_de13_l2_metrics.csv",
    "DeepSeek1.3B_L3": "results/13_de13_l3_metrics.csv",
    "DeepSeek1.3B_L4": "results/14_de13_l4_metrics.csv",
    "DeepSeek1.3B_L5": "results/15_de13_l5_metrics.csv",
}

colors = {
    "Qwen0.5B_L1": "#99ccff",
    "Qwen0.5B_L2": "#6699ff",
    "Qwen0.5B_L3": "#3366ff",
    "Qwen0.5B_L4": "#0033cc",
    "Qwen0.5B_L5": "#001a66",
    
    "Qwen1.5B_L1": "#ff99cc",
    "Qwen1.5B_L2": "#ff6699",
    "Qwen1.5B_L3": "#ff3366",
    "Qwen1.5B_L4": "#cc0033",
    "Qwen1.5B_L5": "#66001a",
    
    "DeepSeek1.3B_L1": "#ffcc99",
    "DeepSeek1.3B_L2": "#ff9966",
    "DeepSeek1.3B_L3": "#ff6600",
    "DeepSeek1.3B_L4": "#cc5200",
    "DeepSeek1.3B_L5": "#662900",
}


# Explanations
metric_explanations = {
    "True Positives": "TP = GT Correct & Model Predicts Correct",
    "True Negatives": "TN = GT Incorrect & Model Predicts Incorrect",
    "False Positives": "FP = GT Incorrect but Model Predicts Correct",
    "False Negatives": "FN = GT Correct but Model Predicts Incorrect",
}

# Load data
data = []
for label, path in files.items():
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        data.append({
            "Model_Setting": label,
            "Metric": row["Metric"],
            "Value": row["Value"]
        })

df_all = pd.DataFrame(data)

# ------------------ Matrix Metrics per model ------------------
matrix_metrics = ["True Positives", "True Negatives", "False Positives", "False Negatives"]
df_matrix = df_all[df_all["Metric"].isin(matrix_metrics)].copy()
df_matrix["Metric_Explained"] = df_matrix["Metric"].map(metric_explanations)

# Plot per model
models = ["Qwen0.5B", "Qwen1.5B", "DeepSeek1.3B"]

for model in models:
    plt.figure(figsize=(14, 6))
    subset = df_matrix[df_matrix["Model_Setting"].str.contains(model)]
    palette_inverted = sns.color_palette("viridis", n_colors=5)[::-1]
    ax = sns.barplot(
        data=subset,
        x="Model_Setting",
        y="Value",
        hue="Metric_Explained",
        palette=palette_inverted
    )
    plt.title(f"{model} - Matrix Metrics (TP, TN, FP, FN)\n(GT = Ground Truth)", fontsize=16)
    plt.xlabel("Setting (L1 → L2 → L3 → L4 → L5)", fontsize=12)
    plt.ylabel("Metric Value", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(title="Metric Explanation", fontsize=10, title_fontsize=11, loc="upper left", bbox_to_anchor=(1.01, 1))

    for p in ax.patches:
        height = p.get_height()
        if not pd.isna(height):
            ax.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=9, color='black', rotation=0, xytext=(0, 3),
                        textcoords='offset points')

    plt.tight_layout()
    plt.savefig(f"plots/{model}_matrix_metrics.png")
    plt.close()

# ------------------ Accuracy ------------------
plt.figure(figsize=(14, 6))
subset_acc = df_all[df_all["Metric"] == "Accuracy"]
bar_colors = [colors[model_setting] for model_setting in subset_acc["Model_Setting"]]
ax2 = sns.barplot(
    data=subset_acc, 
    x="Model_Setting", 
    y="Value", 
    palette=bar_colors
)

plt.title("Accuracy Comparison (L1 → L2 → L3 → L4 → L5)\n(Accuracy = (TP + TN) / Total Samples)", fontsize=16)
plt.xlabel("Model + Setting", fontsize=12)
plt.ylabel("Accuracy", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)

for p in ax2.patches:
    height = p.get_height()
    if not pd.isna(height):
        ax2.annotate(f'{height:.3f}',
                     (p.get_x() + p.get_width() / 2., height),
                     ha='center', va='bottom',
                     fontsize=9, color='black', rotation=0, xytext=(0, 3),
                     textcoords='offset points')

plt.tight_layout()
plt.savefig("plots/accuracy_comparison.png")
plt.close()

print("DONE: Charts saved for matrix metrics (per model) and accuracy.")
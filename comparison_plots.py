import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    "Qwen0.5B_L1": "#99ccff", "Qwen0.5B_L2": "#6699ff", "Qwen0.5B_L3": "#3366ff", "Qwen0.5B_L4": "#0033cc", "Qwen0.5B_L5": "#001a66",
    "Qwen1.5B_L1": "#ff99cc", "Qwen1.5B_L2": "#ff6699", "Qwen1.5B_L3": "#ff3366", "Qwen1.5B_L4": "#cc0033", "Qwen1.5B_L5": "#66001a",
    "DeepSeek1.3B_L1": "#ffcc99", "DeepSeek1.3B_L2": "#ff9966", "DeepSeek1.3B_L3": "#ff6600", "DeepSeek1.3B_L4": "#cc5200", "DeepSeek1.3B_L5": "#662900",
}

matrix_palette = {
    "TP": "#2ca02c",
    "TN": "#1f77b4",
    "FP": "#ff7f0e",
    "FN": "#d62728",
}

label_map = {
    "L1": "L1",
    "L2": "L1+L2",
    "L3": "L1+L2+L3",
    "L4": "L1+L2+L3+L4",
    "L5": "L1+L2+L3+L4+L5"
}

data = []
for label, path in files.items():
    df = pd.read_csv(path)
    total = df[df["Metric"].isin(["True Positives", "True Negatives", "False Positives", "False Negatives"])]["Value"].sum()
    for _, row in df.iterrows():
        val = row["Value"]
        normalized = val / total if row["Metric"] in ["True Positives", "True Negatives", "False Positives", "False Negatives"] else val
        data.append({
            "Model": label.split("_")[0],
            "Level": label.split("_")[1],
            "Label": label_map[label.split("_")[1]],
            "Metric": row["Metric"],
            "Value": val,
            "Normalized": normalized
        })

df_all = pd.DataFrame(data)
df_matrix = df_all[df_all["Metric"].isin(["True Positives", "True Negatives", "False Positives", "False Negatives"])].copy()
df_matrix["Short"] = df_matrix["Metric"].map({
    "True Positives": "TP",
    "True Negatives": "TN",
    "False Positives": "FP",
    "False Negatives": "FN"
})

models = ["Qwen0.5B", "Qwen1.5B", "DeepSeek1.3B"]

for model in models:
    plt.figure(figsize=(14, 6))
    sub = df_matrix[df_matrix["Model"] == model]
    ax = sns.barplot(data=sub, x="Label", y="Normalized", hue="Short", palette=matrix_palette)
    plt.title(f"{model} - Normalized Confusion Matrix", fontsize=16)
    plt.xlabel("Prompt Enrichment", fontsize=14)
    plt.ylabel("Fraction", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(title="Metric", bbox_to_anchor=(1.01, 1), loc="upper left")

    for p in ax.patches:
        val = p.get_height()
        ax.annotate(f"{val:.2f}", (p.get_x() + p.get_width() / 2., val),
                    ha='center', va='bottom', fontsize=11, color='black', xytext=(0, 3),
                    textcoords='offset points')

    plt.tight_layout()
    plt.savefig(f"plots/{model}_matrix.png")
    plt.close()

plt.figure(figsize=(18, 6))
for i, model in enumerate(models, 1):
    sub = df_all[(df_all["Metric"] == "Accuracy") & (df_all["Model"] == model)]
    sub_colors = [colors[f"{model}_{lvl}"] for lvl in sub["Level"]]
    plt.subplot(1, 3, i)
    ax = sns.barplot(data=sub, x="Label", y="Value", palette=sub_colors)
    plt.ylim(0.3, 0.6)
    plt.title(model, fontsize=18)
    plt.xlabel("Enrichment", fontsize=14)
    if i == 1:
        plt.ylabel("Accuracy", fontsize=14)
    else:
        plt.ylabel("")
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for p in ax.patches:
        height = p.get_height()
        if not pd.isna(height):
            ax.annotate(f'{height:.3f}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=11, color='black', xytext=(0, 3),
                        textcoords='offset points')

plt.suptitle("Accuracy Comparison per Model (Cumulative Enrichment)", fontsize=20)
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig("plots/accuracy_comparison.png", dpi=300)
plt.close()

print("DONE")
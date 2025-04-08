import pandas as pd
import random

# File paths
ENRICHED_CSV = "CoderEval4Java_Split5.csv"  # Enriched CSV with all descriptions (5 levels)
KB_CSV = "kb_clean.csv"                     # Cleaned Knowledge Base from kb_checker.py
FINAL_SUBSET_CSV = "subset_final.csv"       # Final subset output

# Load enriched CSV and KB CSV
df_enriched = pd.read_csv(ENRICHED_CSV)
df_kb = pd.read_csv(KB_CSV)

# Convert IDs to strings for merging
df_enriched["_id"] = df_enriched["_id"].astype(str)
df_kb["target_id"] = df_kb["target_id"].astype(str)

# Merge on function ID (inner join)
merged_df = pd.merge(df_enriched, df_kb, left_on="_id", right_on="target_id", how="inner")
merged_df.reset_index(drop=True, inplace=True)

# For each function ID, choose one random model and then select candidate rows from that model.
subset_rows = []
for func_id, group in merged_df.groupby("_id"):
    # Get the list of distinct models from which candidates were generated for this function.
    models = group["generated_by"].unique()
    if len(models) == 0:
        continue  # Skip if no model information is available.
    
    # Randomly choose one model
    selected_model = random.choice(models)
    model_group = group[group["generated_by"] == selected_model]
    
    # For each candidate type, randomly select one if available.
    selected_rows = []
    # For correct candidates (exit_code == 0)
    correct_candidates = model_group[model_group["exit_code"] == 0]
    if not correct_candidates.empty:
        selected_correct = correct_candidates.sample(n=1, random_state=42)
        selected_rows.append(selected_correct)
    # For wrong candidates (exit_code == 1)
    wrong_candidates = model_group[model_group["exit_code"] == 1]
    if not wrong_candidates.empty:
        selected_wrong = wrong_candidates.sample(n=1, random_state=42)
        selected_rows.append(selected_wrong)
    
    if selected_rows:
        subset_rows.append(pd.concat(selected_rows))

if subset_rows:
    final_subset_df = pd.concat(subset_rows)
    final_subset_df.to_csv(FINAL_SUBSET_CSV, index=False, encoding="utf-8")
    print(f"Final subset CSV created: {FINAL_SUBSET_CSV} with {len(final_subset_df)} rows")
else:
    print("No functions processed.")

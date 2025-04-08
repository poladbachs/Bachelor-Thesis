import pandas as pd

# File paths
RAW_KB_CSV = "knowlbase_codereval.csv"   # Provided KB CSV
CLEAN_KB_CSV = "kb_clean.csv"             # Output: Cleaned KB
KB_RESULTS_CSV = "kb_check_results.csv"   # Output: Report of problematic function IDs

# Load the raw KB
df_kb = pd.read_csv(RAW_KB_CSV)

# Filter out rows with missing or empty candidate implementation (assumed in column "method")
df_kb = df_kb[df_kb["method"].notnull() & (df_kb["method"].str.strip() != "")]

# Convert IDs to string for merging later
df_kb["target_id"] = df_kb["target_id"].astype(str)

# Group by target_id
grouped = df_kb.groupby("target_id")
results = []
for func_id, group in grouped:
    has_correct = (group["exit_code"] == 0).any()
    has_wrong = (group["exit_code"] == 1).any()
    results.append({
        "function_id": func_id,
        "has_correct": has_correct,
        "has_wrong": has_wrong,
        "total_candidates": len(group)
    })

results_df = pd.DataFrame(results)
results_df.to_csv(KB_RESULTS_CSV, index=False, encoding="utf-8")
print("KB check results saved to", KB_RESULTS_CSV)

# For downstream work, we output a cleaned KB (without removing functions that lack one type,
# but you might decide to update the KB later if needed)
df_kb_clean = df_kb.copy()
df_kb_clean.to_csv(CLEAN_KB_CSV, index=False, encoding="utf-8")
print("Cleaned KB saved to", CLEAN_KB_CSV)

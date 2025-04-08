import pandas as pd

INPUT_CSV = "merged_full.csv"  # Or use final_dataset.csv if it contains the function name.
OUTPUT_CSV = "problematic_functions.csv"

df = pd.read_csv(INPUT_CSV)

# Use function name; if not available, use function_signature as identifier.
if "name" in df.columns:
    group_key = "name"
else:
    group_key = "function_signature"

results = []
for func, group in df.groupby(group_key):
    has_correct = (group["exit_code"] == 0).any()
    has_wrong = (group["exit_code"] == 1).any()
    if not (has_correct and has_wrong):
        results.append({
            "function": func,
            "has_correct": has_correct,
            "has_wrong": has_wrong,
            "total_candidates": len(group)
        })

if results:
    problematic_df = pd.DataFrame(results)
    problematic_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print("Problematic functions CSV created:", OUTPUT_CSV)
else:
    print("All functions have at least one correct and one wrong candidate.")

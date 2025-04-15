import pandas as pd
import re

# File paths
RAW_KB_CSV = "knowlbase_codereval.csv"   # Provided KB CSV
CLEAN_KB_CSV = "kb_clean.csv"             # Output: Cleaned KB
KB_RESULTS_CSV = "kb_check_results.csv"   # Output: Report of problematic function IDs

def is_trivial(method):
    """
    Check if the implementation code is trivial.
    Returns True if the code is only comments or trivial placeholders (e.g., // TODO).
    """
    if pd.isna(method) or not method.strip():
        return True
    lines = method.splitlines()
    non_comment_lines = []
    for line in lines:
        stripped_line = line.strip()
        # Skip lines that are comments or block comment boundaries.
        if stripped_line.startswith("//") or stripped_line.startswith("/*") or stripped_line.endswith("*/"):
            continue
        # Skip lines that contain only trivial placeholders.
        if "TODO" in stripped_line.upper():
            continue
        non_comment_lines.append(stripped_line)
    code_without_comments = " ".join(non_comment_lines).strip()
    # If nothing remains or only very little code is present, consider it trivial.
    if not code_without_comments or len(code_without_comments) < 10:
        return True
    return False

# Load the raw knowledge base
df_kb = pd.read_csv(RAW_KB_CSV)

# Original filter: remove rows with missing or empty candidate implementations.
df_kb = df_kb[df_kb["method"].notnull() & (df_kb["method"].str.strip() != "")]

# Additional filter: remove trivial implementations (only comments or TODOs).
df_kb = df_kb[~df_kb["method"].apply(is_trivial)]

# Convert IDs to string for merging later
df_kb["target_id"] = df_kb["target_id"].astype(str)

# Group by target_id and generate report on candidate presence
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

# Save the cleaned knowledge base
df_kb_clean = df_kb.copy()
df_kb_clean.to_csv(CLEAN_KB_CSV, index=False, encoding="utf-8")
print("Cleaned KB saved to", CLEAN_KB_CSV)
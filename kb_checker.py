import pandas as pd
import re

<<<<<<< HEAD
=======
# File paths
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
RAW_KB_CSV = "knowlbase_codereval.csv"
CLEAN_KB_CSV = "kb_clean.csv"
KB_RESULTS_CSV = "kb_check_results.csv"

def is_trivial(code):
<<<<<<< HEAD
    if pd.isna(code) or not code.strip():
        return True
    code_lower = code.lower()
    indicators = [
        "todo", "not implemented", "unsupportedoperationexception", "implementation not provided",
        "placeholder", "dummy", "illustration", "example usage", "just print", "you would need to",
        "for illustration", "assume", "assuming", "this would involve", "pass", "here", "there",
        "you", "implement", "this", "do something", "..."
=======
    """
    Flags implementations that are trivial, placeholder, or useless.
    """
    if pd.isna(code) or not code.strip():
        return True

    code_lower = code.lower()
    
    # Detect common placeholder patterns
    indicators = [
        "todo",
        "not implemented",
        "unsupportedoperationexception",
        "implementation not provided",
        "placeholder",
        "dummy",
        "illustration",
        "example usage",
        "just print",
        "you would need to",
        "for illustration",
        "assume",
        "assuming",
        "this would involve",
        "pass",
        "here",
        "there",
        "you",
        "implement",
        "this",
        "do something",
        "..."
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
    ]
    for pattern in indicators:
        if pattern in code_lower:
            return True
<<<<<<< HEAD
    if re.match(r".*public\s+static\s+void\s+main\s*\(\s*String\[\]\s+args\s*\).*", code_lower):
        if len(code_lower.splitlines()) < 10 and "System.out" in code_lower:
            return True
    if "buffer.flip()" in code_lower and "write" not in code_lower:
        return True
=======

    # Check if it looks like a main method without logic
    if re.match(r".*public\s+static\s+void\s+main\s*\(\s*String\[\]\s+args\s*\).*", code_lower):
        if len(code_lower.splitlines()) < 10 and "System.out" in code_lower:
            return True

    # Check if buffer usage is a dummy placeholder
    if "buffer.flip()" in code_lower and "write" not in code_lower:
        return True

    # Strip comments and check code density
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
    lines = code.splitlines()
    non_comment = [line.strip() for line in lines if not line.strip().startswith("//") and len(line.strip()) > 0]
    joined = " ".join(non_comment)
    if len(joined) < 30:
        return True
<<<<<<< HEAD
    return False

# Load full KB (before cleaning)
df_raw = pd.read_csv(RAW_KB_CSV)
df_raw["target_id"] = df_raw["target_id"].astype(str)

# Record how many trivials we filter out per target_id
df_raw["is_trivial"] = df_raw["method"].apply(is_trivial)
trivial_stats = df_raw.groupby("target_id")["is_trivial"].agg(["sum", "count"]).reset_index()
trivial_stats.columns = ["target_id", "num_trivial_removed", "original_total"]
trivial_stats["trivial_ratio_removed"] = trivial_stats["num_trivial_removed"] / trivial_stats["original_total"]

# Clean KB: remove missing/empty and trivial
df_clean = df_raw[~df_raw["is_trivial"]]
df_clean = df_clean[df_clean["method"].notnull() & (df_clean["method"].str.strip() != "")]

# Group by target_id and compute enhanced stats
df_clean["exit_code"] = df_clean["exit_code"].astype(int)
stats = []
for func_id, group in df_clean.groupby("target_id"):
    num_correct = (group["exit_code"] == 0).sum()
    num_incorrect = (group["exit_code"] == 1).sum()
    all_models = group["generated_by"].dropna().unique()
    stats.append({
        "function_id": func_id,
        "has_correct": num_correct > 0,
        "has_wrong": num_incorrect > 0,
        "num_correct": num_correct,
        "num_incorrect": num_incorrect,
        "total_candidates": len(group),
        "models_contributed": len(all_models),
        "all_generated_by": ", ".join(sorted(all_models)),
        "is_balanced": num_correct > 0 and num_incorrect > 0,
=======

    return False

# Load raw KB
df_kb = pd.read_csv(RAW_KB_CSV)

# Drop missing or empty method bodies
df_kb = df_kb[df_kb["method"].notnull() & (df_kb["method"].str.strip() != "")]

# Drop trivial ones
df_kb = df_kb[~df_kb["method"].apply(is_trivial)]

# Report
df_kb["target_id"] = df_kb["target_id"].astype(str)
results = []
for func_id, group in df_kb.groupby("target_id"):
    results.append({
        "function_id": func_id,
        "has_correct": (group["exit_code"] == 0).any(),
        "has_wrong": (group["exit_code"] == 1).any(),
        "total_candidates": len(group)
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
    })
pd.DataFrame(results).to_csv(KB_RESULTS_CSV, index=False)

<<<<<<< HEAD
stats_df = pd.DataFrame(stats)

# Merge in trivial filtering stats
stats_df = stats_df.merge(trivial_stats, how="left", left_on="function_id", right_on="target_id")
stats_df.drop(columns=["target_id"], inplace=True)

# Save reports
df_clean.to_csv(CLEAN_KB_CSV, index=False)
stats_df.to_csv(KB_RESULTS_CSV, index=False)

print(f"✅ Cleaned KB saved to {CLEAN_KB_CSV}")
print(f"✅ KB stats saved to {KB_RESULTS_CSV}")
=======
# Save cleaned KB
df_kb.to_csv(CLEAN_KB_CSV, index=False)
print(f"Cleaned KB saved to {CLEAN_KB_CSV}")
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb

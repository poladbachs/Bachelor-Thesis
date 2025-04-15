import pandas as pd
import re

# File paths
RAW_KB_CSV = "knowlbase_codereval.csv"
CLEAN_KB_CSV = "kb_clean.csv"
KB_RESULTS_CSV = "kb_check_results.csv"

def is_trivial(code):
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
    ]
    for pattern in indicators:
        if pattern in code_lower:
            return True

    # Check if it looks like a main method without logic
    if re.match(r".*public\s+static\s+void\s+main\s*\(\s*String\[\]\s+args\s*\).*", code_lower):
        if len(code_lower.splitlines()) < 10 and "System.out" in code_lower:
            return True

    # Check if buffer usage is a dummy placeholder
    if "buffer.flip()" in code_lower and "write" not in code_lower:
        return True

    # Strip comments and check code density
    lines = code.splitlines()
    non_comment = [line.strip() for line in lines if not line.strip().startswith("//") and len(line.strip()) > 0]
    joined = " ".join(non_comment)
    if len(joined) < 30:
        return True

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
    })
pd.DataFrame(results).to_csv(KB_RESULTS_CSV, index=False)

# Save cleaned KB
df_kb.to_csv(CLEAN_KB_CSV, index=False)
print(f"✅ Cleaned KB saved to {CLEAN_KB_CSV}")

import pandas as pd
import random

# File paths
ENRICHED_CSV = "CoderEval4Java_Split5.csv"         # Enriched CSV with multi-level descriptions (181 function IDs)
KB_CSV = "kb_clean.csv"                             # Cleaned KB with candidate implementations
REFERENCE_CSV = "CoderEval4Java_Raw_Filtered.csv"   # Fallback reference for correct implementations
FINAL_SUBSET_CSV = "subset_360.csv"                 # Final output: 360 rows (179 IDs x 2 candidates (2 incorrect missing))

# Load CSVs
df_enriched = pd.read_csv(ENRICHED_CSV)
df_kb = pd.read_csv(KB_CSV)
df_ref = pd.read_csv(REFERENCE_CSV)

# Convert IDs to strings for consistency
df_enriched["_id"] = df_enriched["_id"].astype(str)
df_kb["target_id"] = df_kb["target_id"].astype(str)
df_ref["_id"] = df_ref["_id"].astype(str)

# Define a local is_trivial function similar to the one in kb_checker.py.
def is_trivial(code):
    if pd.isna(code) or not code.strip():
        return True
    code_lower = code.lower()
    indicators = [
        "todo",
        "placeholder",
        "not implemented",
        "unsupportedoperationexception",
        "throw new unsupportedoperationexception",
        "implementation not provided",
        "pseudo-code",
        "pass",
        "..."
    ]
    for indicator in indicators:
        if indicator in code_lower:
            return True
    # Remove potential comments
    lines = code.splitlines()
    non_comment = []
    for line in lines:
        sline = line.strip()
        if sline.startswith("//") or sline.startswith("/*") or sline.endswith("*/"):
            continue
        non_comment.append(sline)
    cleaned = " ".join(non_comment).strip()
    if not cleaned or len(cleaned) < 10:
        return True
    return False

final_rows = []

for func_id in df_enriched["_id"].unique():
    # Get enriched info (all levels: L1, L2, signature, etc.)
    enriched_subset = df_enriched[df_enriched["_id"] == func_id]
    if enriched_subset.empty:
        print(f"[WARNING] No enriched info for ID {func_id}. Skipping.")
        continue
    enriched_row = enriched_subset.iloc[0].to_dict()

    # Get KB candidates for this function ID.
    kb_group = df_kb[df_kb["target_id"] == func_id]

    ### --- Correct Candidate (exit_code == 0) ---
    kb_corrects = kb_group[kb_group["exit_code"] == 0]
    correct_code = ""
    corr_candidate = None
    if not kb_corrects.empty:
        # Sample until finding a non-trivial candidate
        candidates_list = kb_corrects.to_dict(orient="records")
        non_trivial_corr = [c for c in candidates_list if not is_trivial(c.get("candidate") or c.get("method") or "")]
        if non_trivial_corr:
            corr_candidate = random.choice(non_trivial_corr)
            correct_code = corr_candidate.get("candidate") or corr_candidate.get("method") or ""
    if not correct_code:
        # Fallback: use the reference CSV for correct candidate.
        ref_candidates = df_ref[df_ref["_id"] == func_id]
        if not ref_candidates.empty:
            ref_sample = ref_candidates.sample(n=1, random_state=42).iloc[0].to_dict()
            correct_code = ref_sample.get("code", "")
            corr_candidate = {"exit_code": 0, "generated_by": "reference"}
        else:
            print(f"[WARNING] No correct candidate found for ID {func_id} in KB or reference. Skipping.")
            continue

    # Build the final correct row.
    correct_row = enriched_row.copy()
    correct_row.update({
        "candidate": correct_code,
        "exit_code": corr_candidate.get("exit_code"),
        "generated_by": corr_candidate.get("generated_by")
    })
    final_rows.append(correct_row)

    ### --- Incorrect Candidate (exit_code == 1) ---
    kb_incorrects = kb_group[kb_group["exit_code"] == 1]
    incorrect_code = ""
    inc_candidate = None
    if not kb_incorrects.empty:
        # Try to re-sample until a non-trivial incorrect candidate is found.
        candidates_list = kb_incorrects.to_dict(orient="records")
        non_trivial_incs = [c for c in candidates_list if not is_trivial(c.get("candidate") or c.get("method") or "")]
        if non_trivial_incs:
            inc_candidate = random.choice(non_trivial_incs)
            incorrect_code = inc_candidate.get("candidate") or inc_candidate.get("method") or ""
    if not incorrect_code:
        print(f"[WARNING] No non-trivial incorrect candidate available for ID {func_id}. Skipping this function.")
        continue

    # Build the final incorrect row.
    incorrect_row = enriched_row.copy()
    incorrect_row.update({
        "candidate": incorrect_code,
        "exit_code": inc_candidate.get("exit_code"),
        "generated_by": inc_candidate.get("generated_by")
    })
    final_rows.append(incorrect_row)

# Merge and save the final CSV.
if final_rows:
    final_df = pd.DataFrame(final_rows)
    final_df.to_csv(FINAL_SUBSET_CSV, index=False, encoding="utf-8")
    unique_ids = final_df["_id"].nunique() if "_id" in final_df.columns else "unknown"
    total_rows = len(final_df)
    print(f"Final dataset created: {FINAL_SUBSET_CSV} with {total_rows} rows and {unique_ids} unique function IDs.")
else:
    print("No valid rows were collected.")

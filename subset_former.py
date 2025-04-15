import pandas as pd
import random

# File paths
ENRICHED_CSV = "CoderEval4Java_Split5.csv"         # Enriched CSV: contains 181 function IDs with multi-level descriptions.
KB_CSV = "kb_clean.csv"                             # Cleaned knowledge base with candidate implementations.
REFERENCE_CSV = "CoderEval4Java_Raw_Filtered.csv"   # Fallback reference for correct implementations.
FINAL_SUBSET_CSV = "subset_362.csv"                 # Final output: 362 rows (181 IDs x 2 candidates)

# Load CSVs
df_enriched = pd.read_csv(ENRICHED_CSV)
df_kb = pd.read_csv(KB_CSV)
df_ref = pd.read_csv(REFERENCE_CSV)

# Convert IDs to strings for consistency
df_enriched["_id"] = df_enriched["_id"].astype(str)
df_kb["target_id"] = df_kb["target_id"].astype(str)
df_ref["_id"] = df_ref["_id"].astype(str)

final_rows = []

for func_id in df_enriched["_id"].unique():
    # Get enriched info (with all levels L1, L2, ... signature, etc.) for this function ID.
    enriched_subset = df_enriched[df_enriched["_id"] == func_id]
    if enriched_subset.empty:
        print(f"[WARNING] No enriched info for ID {func_id}. Skipping.")
        continue
    enriched_row = enriched_subset.iloc[0].to_dict()

    # Get all KB candidates (from the cleaned KB) for this function ID.
    kb_group = df_kb[df_kb["target_id"] == func_id]

    ### --- Correct Candidate (exit_code==0) ---
    kb_corrects = kb_group[kb_group["exit_code"] == 0]
    if not kb_corrects.empty:
        corr_candidate = kb_corrects.sample(n=1, random_state=42).iloc[0].to_dict()
        # Attempt to extract the candidate code:
        correct_code = corr_candidate.get("candidate") or corr_candidate.get("method") or ""
    else:
        # Fallback: use the reference CSV.
        ref_candidates = df_ref[df_ref["_id"] == func_id]
        if not ref_candidates.empty:
            ref_sample = ref_candidates.sample(n=1, random_state=42).iloc[0].to_dict()
            correct_code = ref_sample.get("code", "")
            # Build fake candidate fields for consistency.
            corr_candidate = {
                "exit_code": 0,
                "generated_by": "reference"
            }
        else:
            print(f"[WARNING] No correct candidate found for ID {func_id} in KB or reference. Skipping.")
            continue

    correct_row = enriched_row.copy()
    correct_row.update({
        "candidate": correct_code,
        "exit_code": corr_candidate.get("exit_code"),
        "generated_by": corr_candidate.get("generated_by")
    })
    final_rows.append(correct_row)

    ### --- Incorrect Candidate (exit_code==1) ---
    kb_incorrects = kb_group[kb_group["exit_code"] == 1]
    if not kb_incorrects.empty:
        inc_candidate = kb_incorrects.sample(n=1, random_state=42).iloc[0].to_dict()
        # Get candidate code from either the "candidate" or "method" field.
        incorrect_code = inc_candidate.get("candidate") or inc_candidate.get("method") or ""
        incorrect_row = enriched_row.copy()
        incorrect_row.update({
            "candidate": incorrect_code,
            "exit_code": inc_candidate.get("exit_code"),
            "generated_by": inc_candidate.get("generated_by")
        })
        final_rows.append(incorrect_row)
    else:
        print(f"[WARNING] No incorrect candidate available for ID {func_id}. Skipping this function.")
        continue

# Export final CSV if any valid rows were collected.
if final_rows:
    final_df = pd.DataFrame(final_rows)
    final_df.to_csv(FINAL_SUBSET_CSV, index=False, encoding="utf-8")
    unique_ids = final_df["_id"].nunique() if "_id" in final_df.columns else "unknown"
    total_rows = len(final_df)
    print(f"✅ Final dataset created: {FINAL_SUBSET_CSV} with {total_rows} rows and {unique_ids} unique function IDs.")
else:
    print("❌ No valid rows were collected.")

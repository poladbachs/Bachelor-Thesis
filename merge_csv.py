import pandas as pd

# File paths
ENRICHED_CSV = "CoderEval4Java_Split5.csv"
KNOWLEDGE_BASE_CSV = "knowlbase_codereval.csv"
MERGED_OUTPUT_CSV = "merged_full.csv"

# Load both datasets
df_enriched = pd.read_csv(ENRICHED_CSV)
df_knowledge = pd.read_csv(KNOWLEDGE_BASE_CSV)

# Convert IDs to strings for proper merge
df_enriched["_id"] = df_enriched["_id"].astype(str)
df_knowledge["target_id"] = df_knowledge["target_id"].astype(str)

# Merge on function id (inner join to keep only matching rows)
merged_df = pd.merge(df_enriched, df_knowledge, left_on="_id", right_on="target_id", how="inner")

# Save the full merged CSV for later use
merged_df.to_csv(MERGED_OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Merged CSV created: {MERGED_OUTPUT_CSV}")

import pandas as pd

# File paths
MERGED_INPUT_CSV = "merged_full.csv"  # Output from Script 1
SUBSET_OUTPUT_CSV = "subset_merged.csv"

# Load the merged CSV
df = pd.read_csv(MERGED_INPUT_CSV)

# Select the first 30 rows (this will include candidate implementations; note some functions may appear more than once)
subset_df = df.head(30)

# Save the subset CSV
subset_df.to_csv(SUBSET_OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Subset CSV (first 30 rows) created: {SUBSET_OUTPUT_CSV}")
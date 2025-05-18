import pandas as pd
import re

# Input and output CSV paths
INPUT_CSV = "CoderEval/CoderEval4Java_Enriched.csv"
OUTPUT_CSV = "CoderEval/CoderEval4Java_Split.csv"

def parse_enriched_description(text):
    """
    Parse the enriched_description field into its 5 components.
    Ensures correct newlines in examples after the (brief note).
    """
    pattern = (
        r"1\. One-line summary:\s*(.*?)\s*"
        r"2\. Function behavior:\s*(.*?)\s*"
        r"3\. Function signature:\s*(.*?)\s*"
        r"4\. Examples:\s*(.*?)\s*"
        r"5\. Preconditions & Postconditions:\s*(.*)"
    )

    match = re.search(pattern, text, re.DOTALL)
    if match:
        examples = match.group(4).strip()

        # 🔥 **Ensure proper line breaks ONLY after (brief note)**
        examples = re.sub(r"(\(.*?\))\s*", r"\1\n", examples)  # New line after each (brief note)

        return {
            "one_line_summary": match.group(1).strip(),
            "function_behavior": match.group(2).strip(),
            "function_signature": match.group(3).strip(),
            "examples": examples.strip(),
            "precond_postcond": match.group(5).strip(),
        }
    else:
        return {
            "one_line_summary": "",
            "function_behavior": "",
            "function_signature": "",
            "examples": "",
            "precond_postcond": "",
        }

# Load the enriched CSV
df = pd.read_csv(INPUT_CSV)

# Ensure 'enriched_description' column exists
if "enriched_description" not in df.columns:
    raise ValueError("ERROR: 'enriched_description' column not found in CSV!")

# Apply the function to parse the descriptions and fix formatting
parsed_data = df["enriched_description"].astype(str).apply(parse_enriched_description)
parsed_df = pd.DataFrame(parsed_data.tolist())

df = df.drop(columns=["enriched_description"])

# Merge with the original data
df_combined = pd.concat([df, parsed_df], axis=1)

# Save the cleaned CSV
df_combined.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"✅ FINAL FINAL FIX: Properly formatted CSV created at: {OUTPUT_CSV}")

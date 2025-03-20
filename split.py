import pandas as pd
import re

# Input and output CSV paths
INPUT_CSV = "CoderEval4Java_Enriched2.csv"
OUTPUT_CSV = "CoderEval4Java_Split2.csv"

def parse_enriched_description(text):
    """
    Parse the enriched_description field into its 5 components.
    Returns a dictionary with keys:
      - one_line_summary
      - function_behavior
      - function_signature
      - examples
      - precond_postcond
    """
    # Define a regex pattern to capture the content between the markers.
    pattern = (
        r"\*\*1\. One-line summary:\*\*(.*?)"  # group 1
        r"\*\*2\. Function behavior:\*\*(.*?)"  # group 2
        r"\*\*3\. Function signature:\*\*(.*?)"  # group 3
        r"\*\*4\. Examples:\*\*(.*?)"           # group 4
        r"\*\*5\. Preconditions & Postconditions:\*\*(.*)"  # group 5
    )
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return {
            "one_line_summary": match.group(1).strip(),
            "function_behavior": match.group(2).strip(),
            "function_signature": match.group(3).strip(),
            "examples": match.group(4).strip(),
            "precond_postcond": match.group(5).strip(),
        }
    else:
        # If pattern is not found, return empty strings
        return {
            "one_line_summary": "",
            "function_behavior": "",
            "function_signature": "",
            "examples": "",
            "precond_postcond": "",
        }

# Load the enriched CSV
df = pd.read_csv(INPUT_CSV)

# Create new columns by parsing the enriched_description
parsed_data = df["enriched_description"].apply(parse_enriched_description)
# Convert the series of dicts to a DataFrame
parsed_df = pd.DataFrame(parsed_data.tolist())

df = df.drop(columns=["enriched_description"])

# Combine with the original data (if you want to keep other fields too)
df_combined = pd.concat([df, parsed_df], axis=1)

# Save the resulting DataFrame to a new CSV
df_combined.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"✅ Split enriched CSV created: {OUTPUT_CSV}")
import openai
import pandas as pd
import os
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

CSV_INPUT_PATH = "CoderEval4Java_Raw_Filtered.csv"
CSV_OUTPUT_PATH = "CoderEval4Java_Enriched.csv"

df = pd.read_csv(CSV_INPUT_PATH)

def generate_enriched_description(name, code):
    """
    Queries OpenAI GPT model to generate enriched multi-level descriptions for a given function.
    Ensures NO filler phrases, unnecessary intros, or excessive verbosity.
    """
    prompt = f"""
    Function Name: {name}
    Code:
    {code}

    Answer STRICTLY in this format WITHOUT extra text, introductions, or explanations.

    ---
    **1. One-line summary:** (MUST be ultra-short, NO details, NO corner cases.)
    **2. Function behavior:** (Describe how the function works in detail.)
    **3. Function signature:** (Describe the parameters and return type.)
    **4. Examples:** (Show input-output examples.)
    **5. Preconditions & Postconditions:** (Explain constraints, expected outputs, and failure cases.)
    ---

    IMPORTANT RULES:
    - DO NOT include any greeting or opening like “Certainly!” or “Here's your response”.
    - DO NOT add explanations about what you are doing.
    - JUST OUTPUT the descriptions, formatted exactly as specified above.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error processing function '{name}': {e}")
        return "ERROR"

enriched_descriptions = []
for index, row in df.iterrows():
    print(f"Processing function {index + 1}/{len(df)}: {row['name']}")
    
    enriched_desc = generate_enriched_description(row["name"], row["code"])
    
    enriched_descriptions.append(enriched_desc)

    time.sleep(1)

df["enriched_description"] = enriched_descriptions

df.to_csv(CSV_OUTPUT_PATH, index=False, encoding="utf-8")

print(f"Enriched CSV file created: {CSV_OUTPUT_PATH}")
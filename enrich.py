import os
import openai
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY is not set! Check your .env file.")

client = openai.OpenAI(api_key=API_KEY)

CSV_INPUT_PATH = "CoderEval/CoderEval4Java_Raw_Filtered.csv"
CSV_OUTPUT_PATH = "CoderEval/CoderEval4Java_Enriched.csv"

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

    1. One-line summary: (MUST be ultra-short, no corner cases.)
    2. Function behavior: (Max 2 lines describing what the function does.)
    3. Function signature: (Use @param, @return, @throws only if relevant, each on its own line, with a very brief description.
    @param <param_name> <param_type>: <brief parameter description>
    @return <return_type>: <brief return description>
    @throws <exception_type>: <brief exception description>
    Include ONLY the relevant tags. If the method has no parameters, skip @param. If it has no return value, skip @return. If it throws no exceptions, skip @throws.)
    4. Examples: (Provide minimal examples on single lines, no code blocks, no extra symbols, NO backticks:
    input -> output (brief note)
    input -> output (brief note)
    input -> output (brief note)
    )
    5. Preconditions & Postconditions: (Concise constraints and outcomes, max 2 lines.)

    IMPORTANT RULES:
    - Do NOT include any greeting or opening like “Certainly!” or “Here's your response”.
    - Do NOT add code blocks, triple backticks, or lines like “Copy”/“Edit”.
    - Keep everything concise, no bullet points, no extra parentheses.
    - JUST OUTPUT the descriptions in the exact format above.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
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
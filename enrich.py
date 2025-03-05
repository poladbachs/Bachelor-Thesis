import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file BEFORE using them
load_dotenv()

# Get API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OpenAI API key. Ensure it's set in the .env file.")

# Create the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# Paths for input and output JSON
json_path = "CoderEval4Java.json"
output_path = "CoderEval4Java_Enriched.json"

# Read the JSON file
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Check if the JSON has a "RECORDS" key; if not, assume data is a list
if isinstance(data, dict) and "RECORDS" in data:
    records = data["RECORDS"]
else:
    records = data

# IDs to exclude
excluded_ids = {
    "6367667f1a6d9265ec017458", "6367667d1a6d9265ec0173ff", "636766821a6d9265ec0174d2",
    "636767431a6d9265ec017c8d", "6367667c1a6d9265ec0173f7", "6367667c1a6d9265ec0173fb",
    "6367667f1a6d9265ec01745c", "636766801a6d9265ec017477", "636766801a6d9265ec017482",
    "636766811a6d9265ec017496", "636766811a6d9265ec017499", "636766821a6d9265ec0174b3",
    "636766851a6d9265ec017515", "636766a81a6d9265ec01757b", "636766a81a6d9265ec017596",
    "636766ef1a6d9265ec01761a", "636766f81a6d9265ec017748", "636766f81a6d9265ec01774b",
    "636766fe1a6d9265ec017823", "636766fe1a6d9265ec017833", "636767001a6d9265ec01787e",
    "636767001a6d9265ec01787f", "636767071a6d9265ec017962", "636767461a6d9265ec017d17",
    "6367674b1a6d9265ec017dc0", "636767531a6d9265ec017ef1", "636767531a6d9265ec017efb",
    "6367675a1a6d9265ec018010", "636767601a6d9265ec0180fd", "636767611a6d9265ec018106",
    "636767641a6d9265ec01817d", "636767641a6d9265ec018190", "636767691a6d9265ec0181ae",
    "636767781a6d9265ec018238", "636767781a6d9265ec01823d", "636767781a6d9265ec01823e",
    "636767781a6d9265ec018242", "636767791a6d9265ec018257", "636767791a6d9265ec018263",
    "6367677e1a6d9265ec018314", "636767841a6d9265ec0183f2", "636767841a6d9265ec0183ff",
    "636767aa1a6d9265ec01865a", "636767ab1a6d9265ec01867b", "636767dc1a6d9265ec0186c6",
    "636767de1a6d9265ec018706", "636767de1a6d9265ec01871e", "636767de1a6d9265ec018726",
    "636767e11a6d9265ec018790"
}

# Function to call OpenAI GPT to generate enriched descriptions
def generate_enriched_description(name, code):
    prompt = f"""
    Function Name: {name}
    Code:
    {code}

    Generate the following descriptions:
    1. One-sentence summary of the function.
    2. A longer description explaining the function's behavior.
    3. A detailed description of the signature objects, documenting the function's parameters and return type.
    4. Examples of input (i.e., function invocations with specific parameters' values) and corresponding output.
    5. Document pre-conditions and post-conditions.
    """

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an expert code analyst."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1500
)

    enriched_desc = response.choices[0].message.content
    return enriched_desc

# Process each record in the dataset
updated_records = []

for entry in records:
    if not isinstance(entry, dict):
        continue

    function_id = entry.get("_id", "")
    if function_id in excluded_ids:
        continue

    name = entry.get("name", "UnknownFunction")
    code = entry.get("code", "")

    enriched_desc = generate_enriched_description(name, code)
    entry["enriched_description"] = enriched_desc
    updated_records.append(entry)

# Update JSON structure if it originally had a "RECORDS" key
if isinstance(data, dict) and "RECORDS" in data:
    data["RECORDS"] = updated_records
    updated_data = data
else:
    updated_data = updated_records

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(updated_data, f, indent=4)

print(f"Updated JSON saved at {output_path}")
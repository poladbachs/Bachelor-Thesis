import pandas as pd
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-Coder-0.5B-Instruct"
INPUT_CSV = "subset_362_final.csv"
OUTPUT_CSV = "final_dataset_with_predictions.csv"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
model.eval()

def build_evaluation_prompt(row):
    """
    Constructs the evaluation prompt using only Level 1 (one_line_summary) for the description.
    Follows the exact format:
    
    You will be provided with the description ("Description") and the signature ("Signature") of a Java function to implement. 
    You will also see a candidate implementation ("Candidate"). Your role is to evaluate the correctness of the Candidate, providing as output either 0 or 1, and no other text:
    
    0. Wrong Implementation: The implementation does not correctly implement the described function.
    1. Correct Implementation: The implementation correctly implements the described function.
    
    # Description:
    <DESCRIPTION>
    
    # Signature:
    <SIGNATURE>
    
    # Candidate:
    <CANDIDATE>
    
    # Output:
    """
    description = row["one_line_summary"].strip()  # Level 1 only
    signature = row["function_signature"].strip()
    candidate = row["candidate"].strip()
    
    prompt = (
        'You will be provided with the description ("Description") and the signature ("Signature") of a Java function to implement. '
        'You will also see a candidate implementation ("Candidate"). Your role is to evaluate the correctness of the Candidate, providing as output either 0 or 1, and no other text:\n\n'
        '0. Wrong Implementation: The implementation does not correctly implement the described function.\n'
        '1. Correct Implementation: The implementation correctly implements the described function.\n\n'
        '# Description:\n' + description + "\n\n" +
        '# Signature:\n' + signature + "\n\n" +
        '# Candidate:\n' + candidate + "\n\n" +
        '# Output:'
    )
    return prompt

def evaluate_candidate(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    # Set a low temperature for deterministic output.
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=20, do_sample=True, temperature=0.2)
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "# Output:" in output_text:
        generated = output_text.split("# Output:")[-1].strip()
    else:
        generated = output_text.strip()
    if "0" in generated:
        return 0
    elif "1" in generated:
        return 1
    else:
        return None

df = pd.read_csv(INPUT_CSV)

predictions = []
for idx, row in df.iterrows():
    prompt = build_evaluation_prompt(row)
    prediction = evaluate_candidate(prompt)
    predictions.append(prediction)
    print(f"Row {idx+1}/{len(df)}: Prediction = {prediction}")
    time.sleep(1)

df["predicted_exit_code"] = predictions
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"Final dataset with predictions saved as: {OUTPUT_CSV}")

# Compute evaluation metrics
tp = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 0)])
tn = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 1)])
fp = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 0)])
fn = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 1)])
total = len(df)

accuracy = (tp + tn) / total if total > 0 else 0

print("Evaluation Metrics:")
print("True Positives:", tp)
print("True Negatives:", tn)
print("False Positives:", fp)
print("False Negatives:", fn)
print("Accuracy:", accuracy)

import pandas as pd
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# CONFIG
MODEL_NAME = "deepseek-ai/deepseek-coder-1.3b-instruct"
INPUT_CSV = "subset_362_final.csv"
OUTPUT_CSV = "25_de13_nol5.csv"
RAW_OUTPUTS_TXT = "25_de13_nol5_output.txt"
METRICS_CSV = "25_de13_nol5_metrics.csv"
TEMPERATURE = 0.2

# Load model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
model.eval()
def build_prompt(row):
    return f"""You will be provided with the description ("Description") and the signature ("Signature") of a Java function to implement. You will also see a candidate implementation ("Candidate"). Your role is to evaluate the correctness of the Candidate, providing as output either 0 or 1, and no other text:

0. Wrong Implementation: The implementation does not correctly implement the described function.
1. Correct Implementation: The implementation correctly implements the described function.

# Description:
- Summary: {row['one_line_summary']}
- Behavior: {row['function_behavior']}
- Signature Description: {row['function_signature']}
- Examples: {row['examples']}
- Preconditions and Postconditions: {row['precond_postcond']}

# Signature:
{row['candidate'].strip().splitlines()[0]}

# Candidate:
{row['candidate']}

# Output:"""

# Load dataset
df = pd.read_csv(INPUT_CSV)
predictions = []
full_model_outputs = []

# Evaluation loop
for i, row in df.iterrows():
    prompt = build_prompt(row)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=20, do_sample=True, temperature=TEMPERATURE)
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    full_model_outputs.append(output_text)

    if "# Output:" in output_text:
        answer = output_text.split("# Output:")[-1].strip()
    else:
        answer = output_text.strip()
    if "0" in answer:
        predictions.append(0)
    elif "1" in answer:
        predictions.append(1)
    else:
        predictions.append(None)

    print(f"Row {i+1}/{len(df)} -> Prediction: {predictions[-1]}")
    time.sleep(0.5)

# Save full raw model outputs
with open(RAW_OUTPUTS_TXT, "w", encoding="utf-8") as f:
    for idx, output in enumerate(full_model_outputs):
        f.write(f"Row {idx+1}:\n{output}\n\n")

# Save predictions
df["predicted_exit_code"] = predictions
df.to_csv(OUTPUT_CSV, index=False)

tp = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 1)])  # Correct predicted as correct
tn = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 0)])  # Incorrect predicted as incorrect
fp = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 1)])  # Incorrect predicted as correct
fn = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 0)])  # Correct predicted as incorrect
acc = (tp + tn) / len(df)

# Save metrics
metrics = {
    "Metric": ["True Positives", "True Negatives", "False Positives", "False Negatives", "Accuracy"],
    "Value": [tp, tn, fp, fn, acc]
}
metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv(METRICS_CSV, index=False)

print(f"Metrics saved to {METRICS_CSV}")
print(f"Raw model outputs saved to {RAW_OUTPUTS_TXT}")

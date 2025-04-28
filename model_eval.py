import pandas as pd
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
INPUT_CSV = "subset_362_final.csv"
OUTPUT_CSV = "model_eval_qwen15_l1-1.csv"
TEMPERATURE = 0.2

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
model.eval()

def build_prompt(row):
    return f"""You will be provided with the description ("Description") and the signature ("Signature") of a Java function to implement. You will also see a candidate implementation ("Candidate"). Your role is to evaluate the correctness of the Candidate, providing as output either 0 or 1, and no other text:

0. Wrong Implementation: The implementation does not correctly implement the described function.
1. Correct Implementation: The implementation correctly implements the described function.

# Description:
{row['one_line_summary']}

# Signature:
{row['function_signature']}

# Candidate:
{row['candidate']}

# Output:"""

df = pd.read_csv(INPUT_CSV)
predictions = []

for i, row in df.iterrows():
    prompt = build_prompt(row)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=20, do_sample=True, temperature=TEMPERATURE)
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
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

df["predicted_exit_code"] = predictions
df.to_csv(OUTPUT_CSV, index=False)

tp = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 1)])
tn = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 0)])
fp = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 1)])
fn = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 0)])
acc = (tp + tn) / len(df)

# Save evaluation metrics to a CSV file
metrics = {
    "Metric": ["True Positives", "True Negatives", "False Positives", "False Negatives", "Accuracy"],
    "Value": [tp, tn, fp, fn, acc]
}
metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv("model_eval_metrics.csv", index=False)
print("Metrics saved to model_eval_metrics.csv")
import pandas as pd
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

<<<<<<< HEAD
# CONFIG
MODEL_NAME = "deepseek-ai/deepseek-coder-1.3b-instruct"
INPUT_CSV = "subset_362_final.csv"
OUTPUT_CSV = "model_eval_deep13_l2-5.csv"
RAW_OUTPUTS_TXT = "deep13_l2_output_raw-5.txt"
METRICS_CSV = "deep13_l2_metrics-5.csv"
=======
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
INPUT_CSV = "subset_362_final.csv"
OUTPUT_CSV = "model_eval_qwen15_l1-1.csv"
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
TEMPERATURE = 0.2

# Load model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
model.eval()

<<<<<<< HEAD
# Build prompt
=======
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
def build_prompt(row):
    return f"""You will be provided with the description ("Description") and the signature ("Signature") of a Java function to implement. You will also see a candidate implementation ("Candidate"). Your role is to evaluate the correctness of the Candidate, providing as output either 0 or 1, and no other text:

0. Wrong Implementation: The implementation does not correctly implement the described function.
1. Correct Implementation: The implementation correctly implements the described function.

# Description:
{row['one_line_summary']}
<<<<<<< HEAD
{row['function_behavior']}
=======
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb

# Signature:
{row['function_signature']}

# Candidate:
{row['candidate']}

# Output:"""

<<<<<<< HEAD
# Load dataset
df = pd.read_csv(INPUT_CSV)
predictions = []
full_model_outputs = []

# Evaluation loop
=======
df = pd.read_csv(INPUT_CSV)
predictions = []

>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
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
<<<<<<< HEAD

=======
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
    if "0" in answer:
        predictions.append(0)
    elif "1" in answer:
        predictions.append(1)
    else:
        predictions.append(None)
<<<<<<< HEAD

    print(f"Row {i+1}/{len(df)} -> Prediction: {predictions[-1]}")
    time.sleep(0.5)

# Save full raw model outputs
with open(RAW_OUTPUTS_TXT, "w", encoding="utf-8") as f:
    for idx, output in enumerate(full_model_outputs):
        f.write(f"Row {idx+1}:\n{output}\n\n")
=======
    print(f"Row {i+1}/{len(df)} -> Prediction: {predictions[-1]}")
    time.sleep(0.5)
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb

# Save predictions
df["predicted_exit_code"] = predictions
df.to_csv(OUTPUT_CSV, index=False)

<<<<<<< HEAD
tp = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 1)])  # Correct predicted as correct
tn = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 0)])  # Incorrect predicted as incorrect
fp = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 1)])  # Incorrect predicted as correct
fn = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 0)])  # Correct predicted as incorrect
acc = (tp + tn) / len(df)

# Save metrics
=======
tp = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 1)])
tn = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 0)])
fp = len(df[(df["exit_code"] == 0) & (df["predicted_exit_code"] == 1)])
fn = len(df[(df["exit_code"] == 1) & (df["predicted_exit_code"] == 0)])
acc = (tp + tn) / len(df)

# Save evaluation metrics to a CSV file
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
metrics = {
    "Metric": ["True Positives", "True Negatives", "False Positives", "False Negatives", "Accuracy"],
    "Value": [tp, tn, fp, fn, acc]
}
metrics_df = pd.DataFrame(metrics)
<<<<<<< HEAD
metrics_df.to_csv(METRICS_CSV, index=False)

print(f"Metrics saved to {METRICS_CSV}")
print(f"Raw model outputs saved to {RAW_OUTPUTS_TXT}")
=======
metrics_df.to_csv("model_eval_metrics.csv", index=False)
print("Metrics saved to model_eval_metrics.csv")
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb

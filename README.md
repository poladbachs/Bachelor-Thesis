# LLM as Code Correctness Judge (Bachelor Thesis)
![Image](https://github.com/user-attachments/assets/8f18475b-2ae8-4d60-81db-5c59f34137cd)

Evaluate if instruction-tuned LLMs can judge **Java function correctness**.  
Models classify candidate implementations as either **correct (1)** or **wrong (0)**.

---

## 🤖 Models (via Hugging Face)

- [`Qwen/Qwen2.5-Coder-0.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct)  
- [`Qwen/Qwen2.5-Coder-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct)  
- [`deepseek-ai/deepseek-coder-1.3b-instruct`](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct)

Each model was tested across 5 prompt levels (L1–L5) and additional **ablation runs** (removing one level at a time).

---

## 📌 Dataset

- 181 real Java functions (from CoderEval)
- Each paired with 1 correct + 1 incorrect non-trivial implementation → **362 total rows**
- Descriptions enriched to 5 prompt levels using GPT-4o:
  - **L1**: Summary  
  - **L2**: +Behavior  
  - **L3**: +Signature Description  
  - **L4**: +Examples  
  - **L5**: +Pre/Postconditions  

---

## 📊 Evaluation

- LLMs predict binary output (0 or 1) based on prompt + candidate code
- Metrics: Accuracy, TP, TN, FP, FN
- Results:
  - `results/`: 15 full runs (3 models × 5 levels)  
  - `additional_results/`: ablation runs (e.g. without L4 (examples))  
  - `plots/`: visual comparisons (accuracy and confusion)  

---

## 🛠️ Tech Stack

| Tool / Library              | Purpose                                             |
|-----------------------------|-----------------------------------------------------|
| **Python**                  | Core scripting and orchestration                    |
| **Java**                  | Dataset language (functions + candidates)                    |
| **Hugging Face Transformers** | Inference with Qwen and DeepSeek models             |
| **OpenAI API**     | Prompt enrichment for multi-level descriptions      |
| **Pandas**                  | Data manipulation and CSV handling                  |
| **Matplotlib** / **Seaborn**| Accuracy/confusion chart plotting  

---

## 📁 Project Structure

| Path                 | Description                                 |
|----------------------|---------------------------------------------|
| `extract.py`         | Filter raw CoderEval JSON                   |
| `kb_checker.py`      | Clean trivial candidate code                |
| `enrich.py`          | Generate 5-level descriptions (GPT-4o)      |
| `split.py`           | Parse enriched text into columns            |
| `subset_former.py`   | Match correct+incorrect candidates          |
| `patch_subset.py`    | Add 2 missing incorrect cases → 362 rows    |
| `model_eval.py`      | Run Hugging Face LLMs                       |
| `comparison_full.py` | Generate accuracy/confusion plots           |
| `report/`            | LaTeX report source files                   |
| `results/`           | Evaluation outputs (CSV)                    |
| `plots/`             | Accuracy + TP/TN/FP/FN charts               |
| `additional_results/`| Ablation result CSVs                        |
| `dataset/`           | Final 362-row dataset                       |

---

📄 The **Project Report (PDF)** is available in the `report/` folder alongside with LaTeX source files.

---

## ✅ What’s Precomputed

Everything needed to replicate results or create visuals is already included:
- Final dataset → `dataset/subset_362_final.csv`  
- All evaluation outputs → `results/`, `additional_results/`  
- All plots → `plots/`

🟢 You don’t need to rerun scripts unless modifying the dataset or testing new models.

---

## ▶️ Full Replication Guide (Optional)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Extract filtered function set from raw CoderEval JSON
python extract.py

# 3. Generate 5-level enriched descriptions (GPT-4o)
echo OPENAI_API_KEY=sk-... > .env
python enrich.py

# 4. Split enriched descriptions into structured columns
python split.py

# 5. Clean KB by removing trivial/placeholder implementations
python kb_checker.py

# 6. Build evaluation dataset (correct + incorrect per function)
python subset_former.py
python patch_subset.py

# 7. Evaluate any model (edit model_eval.py to set model and output paths)
python model_eval.py

# 8. Plot final accuracy + confusion charts
python comparison_full.py

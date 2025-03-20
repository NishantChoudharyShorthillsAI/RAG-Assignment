import json
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from rouge import Rouge

# Paths to files
GOLDEN_SET_FILE = "../devops_qa_complete.json"  # File with {"question": "...", "answer": "..."}
GENERATED_RESPONSES_FILE = "../generated_answers.json"  # File with {"question": "...", "answer": "..."}
OUTPUT_EXCEL_FILE = "../evaluation_results.xlsx"
OUTPUT_CSV_FILE = "evaluation_results.csv"

# Load models
print("🔄 Loading SentenceTransformer model...")
MODEL_PATH = "./local_paraphrase_model"  # Store locally to avoid re-downloading
if not os.path.exists(MODEL_PATH):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=MODEL_PATH)
model = SentenceTransformer(MODEL_PATH)

rouge = Rouge()

def load_json(file_path):
    """Loads JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ Error: File not found - {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in {file_path}")
        return []

def compute_similarity(golden_answer, generated_answer):
    """Computes ROUGE and Cosine Similarity scores."""
    try:
        # ROUGE Scores
        rouge_scores = rouge.get_scores(generated_answer, golden_answer)[0]
        rouge_1 = rouge_scores["rouge-1"]["f"]
        rouge_2 = rouge_scores["rouge-2"]["f"]
        rouge_l = rouge_scores["rouge-l"]["f"]

        # Cosine Similarity
        golden_embedding = model.encode(golden_answer, convert_to_tensor=True)
        generated_embedding = model.encode(generated_answer, convert_to_tensor=True)
        cosine_score = util.pytorch_cos_sim(golden_embedding, generated_embedding).item()

        return rouge_1, rouge_2, rouge_l, cosine_score
    except Exception as e:
        print(f"⚠️ Error computing similarity: {e}")
        return 0, 0, 0, 0

def evaluate():
    """Compares generated responses with golden set and calculates similarity scores."""
    golden_set = load_json(GOLDEN_SET_FILE)
    generated_responses = load_json(GENERATED_RESPONSES_FILE)

    if not golden_set or not generated_responses:
        print("❌ Error: One or both input files are empty.")
        return

    results = []
    for golden, generated in zip(golden_set, generated_responses):
        question = golden.get("question", "Unknown Question")
        golden_answer = golden.get("answer", "")
        generated_answer = generated.get("answer", "")

        rouge_1, rouge_2, rouge_l, cosine_score = compute_similarity(golden_answer, generated_answer)

        results.append({
            "Question": question,
            "Golden Answer": golden_answer,
            "Generated Answer": generated_answer,
            "ROUGE-1": round(rouge_1, 4),
            "ROUGE-2": round(rouge_2, 4),
            "ROUGE-L": round(rouge_l, 4),
            "Cosine Similarity": round(cosine_score, 4)
        })

    # Save results to Excel and CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    
    try:
        df.to_excel(OUTPUT_EXCEL_FILE, index=False)
        print(f"✅ Results saved in {OUTPUT_EXCEL_FILE} and {OUTPUT_CSV_FILE}")
    except ModuleNotFoundError:
        print(f"⚠️ 'openpyxl' not found. Saving only CSV file: {OUTPUT_CSV_FILE}")

if __name__ == "__main__":
    evaluate()

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set. Please check your .env file.")

# Configure the Gemini AI model
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Paths to files
QUESTIONS_FILE = "questions.json"
EXTRACTED_TEXT_FILE = "./Scrapping/extracted_devops_text.txt"
OUTPUT_FILE = "generated_answers.json"

def load_questions():
    """Loads questions from a JSON file."""
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [item["question"] for item in data if "question" in item]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions: {e}")
        return []

def load_extracted_text():
    """Loads extracted text from the default file."""
    if os.path.exists(EXTRACTED_TEXT_FILE):
        with open(EXTRACTED_TEXT_FILE, "r", encoding="utf-8") as file:
            return file.read()
    return ""

def generate_answers(questions, context):
    """Generates answers for each question using Gemini AI."""
    results = []
    for question in questions:
        print(f"Processing: {question}")
        try:
            response = model.generate_content(f"Context: {context}\n\nQuestion: {question}\n\nAnswer:")
            answer = response.text.strip() if response.text else "No answer generated"
        except Exception as e:
            answer = f"Error generating response: {e}"
        
        results.append({"question": question, "answer": answer})
    
    return results

def save_results(results):
    """Saves generated answers to a JSON file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
    print(f"✅ Results saved in {OUTPUT_FILE}")

def main():
    questions = load_questions()
    if not questions:
        print("No questions found.")
        return

    context = load_extracted_text()
    if not context:
        print("No extracted text found.")
        return

    results = generate_answers(questions, context)
    save_results(results)

if __name__ == "__main__":
    main()

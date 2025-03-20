"""Generate Answers using Gemini AI

This script loads DevOps-related questions from a JSON file and generates answers
using the Gemini 1.5 Flash model. The answers are saved to an output JSON file.

"""

import json
import os
import time
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
INPUT_JSON_FILE = "devops_qa_complete.json"  # JSON file containing {"question": "...", "answer": "..."}
EXTRACTED_TEXT_FILE = "./Scrapping/extracted_devops_text.txt"
OUTPUT_FILE = "generated_answers.json"

def load_extracted_text():
    """Loads extracted text from the default file (context for generation)."""
    if os.path.exists(EXTRACTED_TEXT_FILE):
        with open(EXTRACTED_TEXT_FILE, "r", encoding="utf-8") as file:
            return file.read()
    return ""

def load_questions_one_by_one():
    """Loads questions one by one from a JSON file using a generator (memory-efficient)."""
    try:
        with open(INPUT_JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            for item in data:
                if "question" in item:
                    yield item["question"]  # Yield one question at a time
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions: {e}")
        return

def generate_answer(question, context):
    """Generates an answer for a single question using Gemini AI.
    
    Args:
        question (str): The question to be answered.
        context (str): Extracted text providing additional information.
    
    Returns:
        str: Generated answer or an error message.
    """
    print(f"Processing: {question}")
    try:
        response = model.generate_content(f"Context: {context}\n\nQuestion: {question}\n\nAnswer:")
        return response.text.strip() if response.text else "No answer generated"
    except Exception as e:
        return f"Error generating response: {e}"

def save_answer(question, answer):
    """Appends a generated answer to the output JSON file.
    
    Args:
        question (str): The input question.
        answer (str): The generated answer.
    """
    result = {"question": question, "answer": answer}

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            try:
                results = json.load(file)
                if not isinstance(results, list):
                    results = []
            except json.JSONDecodeError:
                results = []
    else:
        results = []

    results.append(result)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)
    
    print(f"✅ Saved: {question}")

def main():
    """Main function to generate answers for all questions."""
    context = load_extracted_text()
    if not context:
        print("No extracted text found.")
        return

    for question in load_questions_one_by_one():
        answer = generate_answer(question, context)
        save_answer(question, answer)
        print("⏳ Waiting 30 seconds before the next request...")
        time.sleep(30)

if __name__ == "__main__":
    main()

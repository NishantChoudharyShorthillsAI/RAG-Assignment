import PyPDF2
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv  # Import dotenv to load .env file

# Load environment variables from .env file
load_dotenv()

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""

    def extract_text(self):
        """Extracts text from the PDF file."""
        extracted_text = ""
        with open(self.pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
        self.text = extracted_text
        return extracted_text

    def extract_headings_and_content(self):
        """Extracts headings and key content from the extracted text."""
        if not self.text:
            raise ValueError("No text extracted. Run extract_text() first.")
        
        lines = self.text.split("\n")
        important_sections = []
        
        for line in lines:
            if re.match(r'^[0-9]*\.?[0-9]+\s+.*', line) or line.isupper():
                important_sections.append("\n## " + line.strip())
            elif len(line.strip()) > 50:
                important_sections.append(line.strip())
        
        return "\n".join(important_sections)

    def save_to_file(self, output_path, content):
        """Saves extracted content to a text file."""
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(content)
        print(f"Extraction complete. Extracted content saved to {output_path}")

if __name__ == "__main__":
    # Load API key from environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set. Make sure to define it in the .env file.")
    
    genai.configure(api_key=api_key)
    
    pdf_path = "LearningDevOps.pdf"
    output_path = "extracted_devops_text.txt"
    
    extractor = PDFExtractor(pdf_path)
    extracted_text = extractor.extract_text()
    important_content = extractor.extract_headings_and_content()
    extractor.save_to_file(output_path, important_content)
    
    # Generate response using Google Generative AI
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    while True:
        query = input("Ask a question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        response = model.generate_content(f"Context: {important_content}\n\nQuestion: {query}\n\nAnswer:")
        print("Answer:", response.text)

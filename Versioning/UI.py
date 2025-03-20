import PyPDF2
import re
import google.generativeai as genai
import os
import streamlit as st
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

# Streamlit UI
st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("RAG Chatbot - PDF Q&A")

st.sidebar.header("Upload PDF Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    pdf_path = "uploaded.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())
    
    extractor = PDFExtractor(pdf_path)
    extracted_text = extractor.extract_text()
    important_content = extractor.extract_headings_and_content()
    
    st.subheader("Extracted Content")
    st.text_area("Extracted Key Content", important_content, height=300)
    
    # Load API key from environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY is not set. Make sure to define it in the .env file.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        st.sidebar.header("Chat with AI")
        query = st.text_input("Ask a question about the document")
        if st.button("Get Answer"):
            if query:
                response = model.generate_content(f"Context: {important_content}\n\nQuestion: {query}\n\nAnswer:")
                st.subheader("Answer")
                st.write(response.text)
            else:
                st.warning("Please enter a question.")

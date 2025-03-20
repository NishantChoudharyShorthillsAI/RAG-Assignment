import os
import json
import PyPDF2
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Set page configuration FIRST (before any Streamlit commands)
st.set_page_config(layout="wide")

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("GOOGLE_API_KEY is not set. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

DEFAULT_TEXT_FILE = "./Scrapping/extracted_devops_text.txt"
CHAT_HISTORY_FILE = "generated_answer.json"


def extract_text_from_pdf(pdf_file):
    """Extract text content from an uploaded PDF file.

    Args:
        pdf_file (BytesIO): A file-like object containing the uploaded PDF.

    Returns:
        str: Extracted text from the PDF.
    """
    extracted_text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        extracted_text += page.extract_text() + "\n"
    return extracted_text


def load_chat_history():
    """Load chat history from a JSON file.

    Returns:
        list: A list of dictionaries containing question-answer pairs.
    """
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []


def save_chat_history(chat_history):
    """Save chat history to a JSON file.

    Args:
        chat_history (list): A list of dictionaries containing question-answer pairs.
    """
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(chat_history, file, indent=4)


# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()

if "extracted_text" not in st.session_state:
    if os.path.exists(DEFAULT_TEXT_FILE):
        with open(DEFAULT_TEXT_FILE, "r", encoding="utf-8") as file:
            st.session_state.extracted_text = file.read()
    else:
        st.session_state.extracted_text = ""

# Streamlit UI layout
st.title("🔍 DevOps RAG Chatbot")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Chat History")
    if st.session_state.chat_history:
        for qa in reversed(st.session_state.chat_history):
            with st.expander(f"❓ {qa['question']}"):
                st.markdown(f"**Answer:** {qa['answer']}")
    else:
        st.info("No questions asked yet.")

with col2:
    st.subheader("📂 Upload or Use Default PDF")
    uploaded_file = st.file_uploader("Upload a PDF File", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting text from uploaded PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.session_state.extracted_text = extracted_text
    elif not st.session_state.extracted_text:
        st.warning("No PDF uploaded and no default file found!")

    with st.expander("📖 View Extracted Content"):
        st.text_area("Extracted Text", st.session_state.extracted_text, height=300)

    query = st.text_input("❓ Ask a question:")

    if st.button("Get Answer") and query:
        with st.spinner("Generating answer..."):
            response = model.generate_content(
                f"Context: {st.session_state.extracted_text}\n\nQuestion: {query}\n\nAnswer:"
            )
            answer = response.text.strip()

            qa_pair = {"question": query, "answer": answer}
            st.session_state.chat_history.append(qa_pair)
            save_chat_history(st.session_state.chat_history)

            st.success("✅ Answer Generated!")
            st.markdown(f"**Answer:** {answer}")

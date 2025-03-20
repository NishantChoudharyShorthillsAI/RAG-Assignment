import streamlit as st
import PyPDF2
import google.generativeai as genai
import os
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

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    extracted_text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        extracted_text += page.extract_text() + "\n"
    return extracted_text

@st.cache_data
def get_chat_history():
    return []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = get_chat_history()

if "extracted_text" not in st.session_state:
    if os.path.exists(DEFAULT_TEXT_FILE):
        with open(DEFAULT_TEXT_FILE, "r", encoding="utf-8") as file:
            st.session_state.extracted_text = file.read()
    else:
        st.session_state.extracted_text = ""

st.title("🔍 DevOps RAG Chatbot")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Chat History")
    if st.session_state.chat_history:
        for i, qa in enumerate(st.session_state.chat_history[::-1]):
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
            response = model.generate_content(f"Context: {st.session_state.extracted_text}\n\nQuestion: {query}\n\nAnswer:")
            answer = response.text

            st.session_state.chat_history.append({"question": query, "answer": answer})
            get_chat_history().append({"question": query, "answer": answer})  

            st.success("✅ Answer Generated!")
            st.markdown(f"**Answer:** {answer}")

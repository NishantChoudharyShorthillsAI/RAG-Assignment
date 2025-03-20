import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load API key for Gemini AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY is not set. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Load pre-extracted text
DEFAULT_TEXT_FILE = "extracted_devops_text.txt"
if os.path.exists(DEFAULT_TEXT_FILE):
    with open(DEFAULT_TEXT_FILE, "r", encoding="utf-8") as file:
        extracted_text = file.read()
else:
    st.error(f"Default extracted text file '{DEFAULT_TEXT_FILE}' not found.")
    st.stop()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Streamlit UI
st.title("🔍 DevOps RAG Chatbot")
st.markdown("Ask questions based on the extracted DevOps content.")

# Display extracted text (collapsible)
with st.expander("📖 View Extracted Content"):
    st.text_area("Extracted Text", extracted_text, height=300)

# Chat Input
query = st.text_input("❓ Ask a question:", "")

if st.button("Get Answer") and query:
    with st.spinner("Generating answer..."):
        response = model.generate_content(f"Context: {extracted_text}\n\nQuestion: {query}\n\nAnswer:")
        answer = response.text

        # Store question and answer in history
        st.session_state.chat_history.append({"question": query, "answer": answer})

        st.success("✅ Answer Generated!")
        st.markdown(f"**Answer:** {answer}")

# Chat History Section
st.markdown("---")
st.subheader("📝 Chat History")

if st.session_state.chat_history:
    for qa in st.session_state.chat_history[::-1]:  # Show latest first
        with st.expander(f"❓ {qa['question']}"):
            st.markdown(f"**Answer:** {qa['answer']}")
else:
    st.info("No questions asked yet.")

# PDF Chatbot Application

This project is a PDF chatbot application built using a Retrieval-Augmented Generation (RAG) pipeline. The application allows users to interact with PDF documents through natural language queries, providing accurate and context-aware responses.

## Features
- **PDF Parsing**: Extracts text and metadata from PDF files.
- **RAG Pipeline**: Combines retrieval-based and generative AI techniques for enhanced response accuracy.
- **Natural Language Interface**: Enables intuitive interaction with documents.
- **Customizable Knowledge Base**: Supports adding multiple PDFs for querying.

## How It Works
1. **PDF Ingestion**: Upload PDF documents to the application.
2. **Text Extraction**: Extracts and preprocesses text from the uploaded PDFs.
3. **Retrieval**: Searches for relevant document sections using a vector database.
4. **Generation**: Uses a language model to generate responses based on retrieved content.

## Requirements
- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation
1. Clone the repository:
    ```bash
    git clone "GitHub link"
    cd projectRaG
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Start the application:
    ```bash
    stremlite run UI4.py
    ```
2. Upload a PDF and start asking questions.


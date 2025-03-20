"""FAISS Embedding Generator

This module reads extracted text, generates sentence embeddings using a 
pre-trained model, and stores them in a FAISS index for efficient retrieval.
"""

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FAISSEmbeddingGenerator:
    """Generates and stores embeddings in a FAISS index from input text."""

    def __init__(self, input_text_path, embedding_output_path, model_name="all-MiniLM-L6-v2"):
        """Initialize the FAISS embedding generator.

        Args:
            input_text_path (str): Path to the input text file.
            embedding_output_path (str): Path where the FAISS index will be saved.
            model_name (str, optional): Pre-trained sentence transformer model. Defaults to "all-MiniLM-L6-v2".
        """
        self.input_text_path = input_text_path
        self.embedding_output_path = embedding_output_path
        self.model = SentenceTransformer(model_name)
        self.index = None

    def read_extracted_text(self):
        """Reads the extracted text from the input file.

        Returns:
            list[str]: A list of lines from the extracted text file.
        """
        with open(self.input_text_path, "r", encoding="utf-8") as file:
            return file.readlines()

    def generate_embeddings(self, text_lines):
        """Generates embeddings for the given text lines.

        Args:
            text_lines (list[str]): List of text lines to embed.

        Returns:
            np.ndarray: NumPy array of generated embeddings.
        """
        return self.model.encode(text_lines, convert_to_numpy=True)

    def create_faiss_index(self, embeddings):
        """Creates a FAISS index from the generated embeddings.

        Args:
            embeddings (np.ndarray): NumPy array of sentence embeddings.
        """
        d = embeddings.shape[1]  # Dimension of embeddings
        self.index = faiss.IndexFlatL2(d)  # Create FAISS index
        self.index.add(embeddings)  # Add embeddings to index

    def save_faiss_index(self):
        """Saves the FAISS index to the specified file."""
        if self.index is not None:
            faiss.write_index(self.index, self.embedding_output_path)
            print(f"FAISS index created and saved to {self.embedding_output_path}")
        else:
            raise RuntimeError("Error: FAISS index has not been created.")

    def run(self):
        """Runs the embedding generation and FAISS index creation process."""
        text_lines = self.read_extracted_text()
        embeddings = self.generate_embeddings(text_lines)
        self.create_faiss_index(embeddings)
        self.save_faiss_index()


if __name__ == "__main__":
    INPUT_TEXT_PATH = "../Scrapping/extracted_devops_text.txt"
    EMBEDDING_OUTPUT_PATH = "./devops_faiss_index"

    generator = FAISSEmbeddingGenerator(INPUT_TEXT_PATH, EMBEDDING_OUTPUT_PATH)
    generator.run()
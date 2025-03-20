"""PDF Extractor Module

This module extracts text and headings from a given PDF file.
"""

import re
import PyPDF2


class PDFExtractor:
    """A class for extracting text and structured content from PDF files."""

    def __init__(self, pdf_path):
        """Initialize the PDFExtractor with the path to a PDF file.

        Args:
            pdf_path (str): The path to the PDF file.
        """
        self.pdf_path = pdf_path
        self.text = ""

    def extract_text(self):
        """Extracts text from the PDF file and stores it in `self.text`.

        Returns:
            str: The extracted text from the PDF.
        """
        extracted_text = ""
        try:
            with open(self.pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{self.pdf_path}' was not found.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while reading the PDF: {e}")

        self.text = extracted_text
        return extracted_text

    def extract_headings_and_content(self):
        """Extracts headings and key content from the extracted text.

        Headings are identified by number patterns (e.g., '1.1 Title') or uppercase text.
        Key content is extracted if the line is sufficiently long.

        Returns:
            str: Extracted headings and important content formatted as Markdown.
        """
        if not self.text:
            raise ValueError("No text extracted. Run extract_text() first.")

        lines = self.text.split("\n")
        important_sections = []

        for line in lines:
            stripped_line = line.strip()
            if re.match(r"^[0-9]*\.?[0-9]+\s+.*", stripped_line) or stripped_line.isupper():
                important_sections.append(f"\n## {stripped_line}")
            elif len(stripped_line) > 50:
                important_sections.append(stripped_line)

        return "\n".join(important_sections)

    def save_to_file(self, output_path, content):
        """Saves extracted content to a text file.

        Args:
            output_path (str): The path where the extracted content should be saved.
            content (str): The content to write into the file.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(content)
            print(f"Extraction complete. Extracted content saved to {output_path}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while saving the file: {e}")


if __name__ == "__main__":
    PDF_PATH = "LearningDevOps.pdf"
    OUTPUT_PATH = "extracted_devops_text.txt"

    extractor = PDFExtractor(PDF_PATH)
    extractor.extract_text()
    important_content = extractor.extract_headings_and_content()
    extractor.save_to_file(OUTPUT_PATH, important_content)

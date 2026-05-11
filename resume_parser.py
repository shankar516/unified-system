import pdfplumber
import pytesseract
import io
import numpy as np
from PIL import Image

# NOTE: You must have Tesseract-OCR installed on your system and added to PATH.
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(file_stream):
    """
    Extracts text from a PDF file stream using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        return f"Error reading PDF: {e}"
    
    return text

def extract_text_from_image(file_stream):
    """
    Extracts text from an image file stream using Tesseract OCR.
    """
    try:
        image = Image.open(file_stream)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error reading Image (Ensure Tesseract is installed): {e}"

def parse_resume(uploaded_file):
    """
    Main entry point to parse resume based on file type.
    """
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
        # If PDF text is empty, it might be a scanned PDF (image only)
        if not text.strip():
            # Fallback to OCR on PDF pages (simplified: converting pages to images would be needed)
            # For this MVP, we return a message or handle minimal logic
            return "[Unable to extract text. This might be a scanned PDF. Please upload an Image format or a text-based PDF.]"
        return text
    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        return extract_text_from_image(uploaded_file)
    else:
        return "Unsupported file format."

# AI Resume Analyzer & Career Coach

This application parses resumes (PDF/Image), analyzes them to identify skills and domains, conducts a mock interview for the identified domain, and generates a career roadmap.

## Features

- **Resume Parsing**: Supports Text-based PDFs and Image-based PDFs/Images (OCR via EasyOCR).
- **Analysis**: Extracts summary, skills, and suggested domain using GPT.
- **Mock Interview**: Asks dynamic questions based on the domain and evaluates your answers.
- **Roadmap Generator**: Creates a personalized learning path.

## Setup

1. **Install Dependencies**
   Ensure you have Python installed.

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**

   ```bash
   streamlit run app.py
   ```

3. **API Key**
   You will need an OpenAI API Key to use the AI features. Enter it in the sidebar when the app launches.

## Technologies Used

- **Streamlit**: For the web interface.
- **LangChain**: For creating AI workflows.
- **OpenAI**: For intelligence (Analysis, Q&A).
- **pdfplumber**: For PDF text extraction.
- **EasyOCR**: For Optical Character Recognition.

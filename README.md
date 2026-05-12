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
- 
-**OUTPUT'S:**
- -1.Registration Page, 2.Login Page, 3.Resume Analysis Dashboard, 4.Domain Specific Adaptive MCQ’s, 5.Generating Personalization Roadmap, 6.Interactive AI assistive mode
<img width="978" height="541" alt="image" src="https://github.com/user-attachments/assets/244b9075-21ad-4004-bcb7-6621427ada42" />
<img width="951" height="454" alt="image" src="https://github.com/user-attachments/assets/43b83dea-377c-46b0-8b1c-ba7cc462558a" />
<img width="980" height="511" alt="image" src="https://github.com/user-attachments/assets/01a6cbb5-2034-4cad-bf87-86dfdec3f9d3" />
<img width="961" height="488" alt="image" src="https://github.com/user-attachments/assets/2e4f7334-eb6c-4dac-9258-f6fc1c75c42c" />
<img width="889" height="457" alt="image" src="https://github.com/user-attachments/assets/7e71ed84-0cb2-421b-bf05-55230567292c" />
<img width="907" height="481" alt="image" src="https://github.com/user-attachments/assets/4c587588-5192-4f39-b362-bd6c337cb27b" />







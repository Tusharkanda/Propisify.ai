# AI Proposal Writer - Hackathon Demo

## Overview
This project is an AI-powered proposal generation tool built for hackathons and rapid prototyping. It uses OCR, vector search, and the OpenAI API to help you upload, search, and generate business proposals quickly.

## Features
- Upload and process historical proposals (PDF, image, or text)
- Extract text and metadata using OCR and parsing
- Store and search proposals using ChromaDB vector database
- Generate new proposals with OpenAI GPT models
- Edit and export proposals to Word documents
- Demo mode with sample data for quick testing

## Project Structure
- `app.py` - Main Streamlit application
- `ocr_processor.py` - OCR and PDF/image text extraction
- `data_manager.py` - Vector database management (ChromaDB)
- `ai_generator.py` - OpenAI-based proposal generation
- `document_parser.py` - Section and metadata extraction from text
- `document_exporter.py` - Export proposals to Word documents
- `test_app.py` - Script to test all modules and workflow
- `sample_data/` - Folder with sample proposal texts
- `requirements.txt` - Python dependencies

## Setup Instructions
1. **Clone the repository and navigate to the project folder.**
2. **Create a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **Install Tesseract OCR:**
   - Download from https://github.com/tesseract-ocr/tesseract
   - Add Tesseract to your system PATH if needed.
5. **Get an OpenAI API key:**
   - Sign up at https://platform.openai.com/
   - Create an API key and keep it safe.

## Running the Application
```
streamlit run app.py
```
- Enter your OpenAI API key in the sidebar.
- Upload or use sample proposals.
- Generate, edit, and export proposals.

## Running Tests
```
python test_app.py
```
- This will test each module and the full workflow.

## Troubleshooting
- **Tesseract not found:** Make sure Tesseract is installed and in your PATH.
- **OpenAI errors:** Check your API key and usage limits.
- **ChromaDB issues:** Delete the `chromadb_data` folder to reset the database.
- **File errors:** Ensure your files are in supported formats (.pdf, .png, .jpg, .jpeg, .txt).

## License
MIT License. For hackathon/demo use only.

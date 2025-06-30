from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import re
import logging
from typing import Union, List

class OCRProcessor:
    def __init__(self):
        """Initialize OCR Processor with basic logging setup"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_text_from_image(self, image_file) -> str:
        """
        Extract text from an uploaded image file using OCR.
        
        Args:
            image_file: Streamlit uploaded image file object
        
        Returns:
            str: Extracted text from the image
        """
        try:
            # Read image from uploaded file bytes
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert image to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            return self.clean_extracted_text(text)
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise Exception(f"Failed to process image: {str(e)}")

    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extract text from an uploaded PDF file using OCR.
        
        Args:
            pdf_file: Streamlit uploaded PDF file object
        
        Returns:
            str: Combined extracted text from all pages
        """
        try:
            pdf_file.seek(0)
            images = convert_from_bytes(pdf_file.read())
            
            # Extract text from each page
            extracted_texts: List[str] = []
            for page_num, image in enumerate(images, 1):
                try:
                    text = pytesseract.image_to_string(image)
                    extracted_texts.append(text)
                except Exception as e:
                    self.logger.warning(f"Error processing page {page_num}: {str(e)}")
                    continue
            
            # Combine all extracted text
            combined_text = "\n\n".join(extracted_texts)
            return self.clean_extracted_text(combined_text)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")

    def clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text from OCR
        
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
            
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # Only if confidence is low
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        return text

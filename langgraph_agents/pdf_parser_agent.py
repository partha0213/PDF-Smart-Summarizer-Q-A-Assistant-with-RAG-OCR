import os
# Set OpenMP environment variable before importing other libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import fitz  # PyMuPDF
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFParserAgent:
    """Agent for parsing PDFs and extracting text content"""
    
    def process(self, pdf_path: str) -> tuple[List[Dict], Optional[str]]:
        """
        Process a PDF file and extract text from each page.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            tuple[List[Dict], Optional[str]]: (pages_info, error_message)
            - pages_info: list of dictionaries containing page information
                Each dictionary has:
                - page_num: page number
                - text: extracted text content
            - error_message: None if successful, error description if failed
        """
        try:
            # Verify file exists
            if not Path(pdf_path).exists():
                return [], "PDF file not found"

            doc = fitz.open(pdf_path)
            if doc.is_encrypted:
                return [], "PDF is encrypted. Please provide an unencrypted PDF."
            if not doc.page_count:
                return [], "PDF appears to be empty"

            pages_info = []
            for i, page in enumerate(doc):
                try:
                    # Try normal text extraction
                    text = page.get_text().strip()
                    page_info = {
                        "page_num": i + 1,
                        "text": text if text else f"[Empty page {i+1}]"
                    }
                    pages_info.append(page_info)
                    
                    if not text:
                        logger.warning(f"Empty text content on page {i+1}")
                except Exception as e:
                    logger.error(f"Error processing page {i+1}: {e}")
                    pages_info.append({
                        "page_num": i + 1,
                        "text": f"[Error reading page {i+1}]"
                    })

            doc.close()
            
            # Check if we have any actual text content
            if not any(page["text"] for page in pages_info if not page["text"].startswith("[")):
                return [], "No readable text content found in the PDF"
                
            return pages_info, None
            
        except fitz.FileDataError:
            error_msg = "The file appears to be corrupted or is not a valid PDF"
            logger.error(error_msg)
            return [], error_msg
        except Exception as e:
            error_msg = f"Failed to parse PDF: {str(e)}"
            logger.error(error_msg)
            return [], error_msg

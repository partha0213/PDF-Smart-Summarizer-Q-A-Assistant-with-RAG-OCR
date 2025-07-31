from pathlib import Path
import fitz  # PyMuPDF

class RouterAgent:
    """Agent that decides whether OCR is needed for a PDF"""
    
    def check_needs_ocr(self, pdf_path: str) -> bool:
        """
        Check if a PDF needs OCR by analyzing its content
        Returns True if OCR is needed, False otherwise
        """
        doc = fitz.open(pdf_path)
        needs_ocr = False

        for page in doc:
            # Get text from the page
            text = page.get_text()
            
            # If a page has no text but has images, it likely needs OCR
            if not text.strip() and len(page.get_images()) > 0:
                needs_ocr = True
                break

        doc.close()
        return needs_ocr

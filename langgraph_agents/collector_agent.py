from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CollectorAgent:
    """Agent for collecting and merging text from different sources"""
    
    def merge(self, state: Dict) -> str:
        """
        Merge text from PDF parsing and OCR
        Returns combined text
        """
        try:
            texts = []
            
            # Extract text from PDF pages
            pages = state.get("pages", [])
            if not pages:
                logger.warning("No pages found in state")
            
            # Process each page
            for page in pages:
                if not isinstance(page, dict):
                    logger.warning(f"Invalid page format: {type(page)}")
                    continue
                    
                text = page.get("text", "").strip()
                if text and not text.startswith("["):  # Skip error messages
                    texts.append(text)
            
            # Add OCR text if available
            ocr_text = state.get("ocr_text", "").strip()
            if ocr_text:
                texts.append(ocr_text)
            
            # Validate and combine texts
            if not texts:
                logger.warning("No text content collected")
                return ""
                
            # Combine all texts with proper spacing
            return "\n\n".join(text for text in texts if text.strip())
            
        except Exception as e:
            logger.error(f"Error merging text: {str(e)}")
            raise

import os
# Set OpenMP environment variable before importing other libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from typing import List, Dict
import numpy as np
import time
import logging
import easyocr
from config import OCR_LANGUAGES

logger = logging.getLogger(__name__)

class OCRAgent:
    """Agent for performing OCR on images using EasyOCR"""
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRAgent, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if OCRAgent._reader is None:
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Initialize EasyOCR reader
                    OCRAgent._reader = easyocr.Reader(OCR_LANGUAGES)
                    break
                except Exception as e:
                    if "process cannot access the file" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1}: EasyOCR initialization failed. Retrying in {retry_delay} seconds...")
                        # Try to clean up temp files
                        self._cleanup_temp_files()
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to initialize EasyOCR after {max_retries} attempts: {str(e)}")
                        raise
        
        self.reader = OCRAgent._reader
    
    def _cleanup_temp_files(self):
        """Attempt to clean up temporary files"""
        temp_paths = [
            os.path.expanduser("~/.EasyOCR/model/temp.zip"),
            os.path.expanduser("~/.EasyOCR/model/temp")
        ]
        for path in temp_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Cleaned up temporary file: {path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {path}: {str(e)}")
    
    def process(self, pages: List[Dict]) -> str:
        """
        Process images from PDF pages using OCR
        Returns concatenated OCR text
        """
        ocr_texts = []
        
        for page in pages:
            # Skip if page has sufficient text
            if len(page["text"].strip()) > 100:  # Arbitrary threshold
                continue
                
            # Process images on the page
            for img_info in page["images"]:
                try:
                    # Extract image data
                    image = img_info["image"]
                    if not image:
                        logger.warning(f"Empty image on page {page['page_num']}")
                        continue
                        
                    # Convert image data if needed
                    if isinstance(image, (bytes, bytearray)):
                        from PIL import Image
                        import io
                        image = Image.open(io.BytesIO(image))
                    
                    # Perform OCR with timeout
                    try:
                        results = self.reader.readtext(image, timeout=30)  # 30 seconds timeout
                        
                        # Extract text from results
                        texts = [result[1] for result in results]
                        if texts:
                            ocr_texts.extend(texts)
                            logger.info(f"Successfully extracted text from image on page {page['page_num']}")
                        else:
                            logger.warning(f"No text found in image on page {page['page_num']}")
                    
                    except Exception as ocr_error:
                        logger.error(f"OCR error on page {page['page_num']}: {str(ocr_error)}")
                        continue
                
                except Exception as e:
                    logger.error(f"Error processing image on page {page['page_num']}: {str(e)}")
                    continue
        
        return "\n".join(ocr_texts)

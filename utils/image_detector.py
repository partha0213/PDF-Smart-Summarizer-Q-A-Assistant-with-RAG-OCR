from pathlib import Path
import fitz
from typing import List, Dict

def detect_images_in_pdf(pdf_path: Path) -> List[Dict]:
    """
    Detect images in PDF and their properties
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of dictionaries containing image information
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            image_info = {
                "page_num": page_num,
                "image_index": img_index,
                "width": base_image["width"],
                "height": base_image["height"],
                "colorspace": base_image["colorspace"]
            }
            images.append(image_info)
    
    doc.close()
    return images

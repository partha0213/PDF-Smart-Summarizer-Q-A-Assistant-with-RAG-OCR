from pathlib import Path
from typing import Union, BinaryIO
import magic

def is_valid_pdf(file_content: Union[bytes, BinaryIO]) -> bool:
    """
    Check if the file content is a valid PDF
    
    Args:
        file_content: File content as bytes or file-like object
        
    Returns:
        bool: True if valid PDF, False otherwise
    """
    try:
        # Get file mime type
        mime = magic.from_buffer(file_content, mime=True)
        return mime == 'application/pdf'
    except Exception:
        return False

def save_temp_pdf(file_content: bytes, temp_dir: Path = Path('.')) -> Path:
    """
    Save uploaded file content as temporary PDF
    
    Args:
        file_content: PDF file content in bytes
        temp_dir: Directory to save temp file
        
    Returns:
        Path: Path to saved temporary file
    """
    temp_path = temp_dir / 'temp.pdf'
    temp_path.write_bytes(file_content)
    return temp_path

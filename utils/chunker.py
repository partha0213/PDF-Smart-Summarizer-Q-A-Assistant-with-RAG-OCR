from typing import List
import re

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks of specified size
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Clean text and standardize newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Initialize chunks
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # If not at start, include overlap
        if start > 0:
            start = start - overlap
            
        # Get chunk
        chunk = text[start:end].strip()
        
        # Adjust chunk boundaries to respect sentence endings
        if end < len(text):
            # Try to end at sentence boundary
            sentence_end = re.search(r'[.!?]\s+[A-Z]', chunk)
            if sentence_end:
                chunk = chunk[:sentence_end.start() + 1]
                end = start + len(chunk)
        
        chunks.append(chunk)
        start = end
    
    return chunks

from typing import List, Dict
import numpy as np
import logging
from openai import OpenAI
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class EmbeddingAgent:
    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"Initialized OpenAI client for embeddings: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap, optimized for OpenAI's token limits"""
        chunks = []
        sentences = text.replace('\n', ' ').split('.')
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            # Rough estimation: 4 characters per token
            sentence_size = len(sentence) // 4
            
            if current_size + sentence_size > CHUNK_SIZE:
                if current_chunk:  # Save current chunk
                    chunks.append(' '.join(current_chunk))
                    # Keep last part for overlap
                    overlap_size = len(current_chunk) // 3  # ~33% overlap
                    current_chunk = current_chunk[-overlap_size:] if overlap_size > 0 else []
                    current_size = sum(len(s) // 4 for s in current_chunk)
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def create(self, text: str) -> Dict:
        """
        Create embeddings for text chunks
        Returns dictionary with vectors and metadata
        """
        try:
            if not text or not text.strip():
                raise ValueError("Empty text provided")
            
            # Split text into chunks
            chunks = self._chunk_text(text)
            if not chunks:
                raise ValueError("No chunks created from text")
            
            # Generate embeddings for each chunk
            embeddings = []
            successful_chunks = []
            
            for chunk in chunks:
                if not chunk.strip():
                    continue
                    
                try:
                    # Generate embedding using OpenAI
                    response = self.client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=chunk
                    )
                    embedding = np.array(response.data[0].embedding)
                    embeddings.append(embedding)
                    successful_chunks.append(chunk)
                except Exception as e:
                    logger.error(f"Error generating embedding: {str(e)}")
                    continue
            
            if not embeddings:
                raise ValueError("Failed to generate any valid embeddings")
            
            # Convert to numpy array and validate
            vectors = np.array(embeddings)
            if vectors.shape[0] == 0:
                raise ValueError("Empty vectors array")
            if vectors.shape[0] != len(successful_chunks):
                raise ValueError("Mismatch between vectors and chunks count")
            
            # Return embeddings, chunks and text directly as a tuple for vector store
            return vectors, successful_chunks, [text] * len(successful_chunks)  # Each chunk maps back to the original text
            
        except Exception as e:
            logger.error(f"Error in embedding creation: {str(e)}")
            raise

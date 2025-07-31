import faiss
import numpy as np
import os
import pickle
import logging
from pathlib import Path
from typing import List, Optional
from config import VECTOR_STORE_DIR, FAISS_INDEX_PATH, VECTOR_METADATA_PATH

logger = logging.getLogger(__name__)

class VectorStoreAgent:
    """Agent for managing the FAISS vector store"""
    
    def __init__(self):
        """Initialize vector store with default paths"""
        self.vector_store_path = VECTOR_STORE_DIR
        self.index_path = FAISS_INDEX_PATH
        self.metadata_path = VECTOR_METADATA_PATH
        
        # Create directory if it doesn't exist
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.index = None
        self.metadata = {"chunks": [], "texts": []}
        
        # Load existing data if available
        self._load_existing_store()

    def clear(self):
        """Clear the vector store and metadata"""
        try:
            if self.index_path.exists():
                os.remove(self.index_path)
            if self.metadata_path.exists():
                os.remove(self.metadata_path)
            self.index = None
            self.metadata = {"chunks": [], "texts": []}
            logger.info("Vector store cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False
    
    def _load_existing_store(self):
        """Load existing index and metadata if they exist"""
        try:
            if self.index_path.exists() and self.metadata_path.exists():
                try:
                    self.index = faiss.read_index(str(self.index_path))
                    with open(self.metadata_path, "rb") as f:
                        self.metadata = pickle.load(f)
                    
                    # Validate metadata structure
                    if not isinstance(self.metadata, dict) or "chunks" not in self.metadata or "texts" not in self.metadata:
                        raise ValueError("Invalid metadata structure")
                    
                    chunk_count = len(self.metadata["chunks"])
                    if chunk_count > 0:
                        logger.info(f"Loaded existing store with {chunk_count} chunks")
                    else:
                        logger.warning("Loaded store but it contains no chunks")
                        
                except (EOFError, ValueError) as e:
                    logger.error(f"Corrupted store files, reinitializing: {e}")
                    self._reinitialize_store()
                    
        except Exception as e:
            logger.error(f"Error loading existing store: {e}")
            self._reinitialize_store()
            
    def _reinitialize_store(self):
        """Reinitialize the store with empty state"""
        self.index = None
        self.metadata = {"chunks": [], "texts": [], "full_text": ""}
    
    def store(self, embeddings: List[np.ndarray], chunks: List[str], texts: List[str]) -> bool:
        """
        Store vectors and metadata in FAISS
        
        Args:
            embeddings: List of embedding vectors
            chunks: List of text chunks corresponding to the embeddings
            texts: List of original texts
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert input data to correct format
            embeddings_array = np.array(embeddings)
            
            # Input validation
            if len(embeddings_array) != len(chunks) or len(chunks) != len(texts):
                raise ValueError("Length mismatch between embeddings, chunks, and texts")
            
            # Create new index if doesn't exist
            if self.index is None:
                self.index = faiss.IndexFlatL2(embeddings_array.shape[1])
            
            # Add vectors to index
            self.index.add(embeddings_array)
            
            # Update metadata
            self.metadata["chunks"].extend(chunks)
            self.metadata["texts"].extend(texts)
            
            # Save index and metadata with fsync for durability
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
                f.flush()
                os.fsync(f.fileno())
                
            logger.debug(f"Metadata after store: chunks={len(self.metadata['chunks'])}, texts={len(self.metadata['texts'])}")
            
            logger.info(f"Successfully stored {len(embeddings)} vectors")
            return True

        except Exception as e:
            logger.error(f"Error storing vectors: {e}")
            return False
            
    def search(self, query_vector: np.ndarray, k: int = 5) -> dict:
        """
        Search for similar vectors in the store
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            dict with results and metadata:
                - success: bool indicating if search was successful
                - distances: list of distances for each result
                - results: list of dicts containing:
                    - chunk: the text chunk
                    - text: the original text
                - error: error message if success is False
        """
        try:
            if self.index is None:
                raise ValueError("No index exists")

            # Search index
            query_vector = query_vector.reshape(1, -1)
            distances, indices = self.index.search(query_vector, k)
            
            # Get corresponding chunks
            results = []
            for idx in indices[0]:
                if idx < len(self.metadata["chunks"]):
                    results.append({
                        "chunk": self.metadata["chunks"][idx],
                        "text": self.metadata["texts"][idx] if idx < len(self.metadata["texts"]) else ""
                    })

            return {
                "success": True,
                "distances": distances[0].tolist(),
                "results": results
            }

        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return {
                "success": False,
                "error": str(e),
                "distances": [],
                "results": []
            }

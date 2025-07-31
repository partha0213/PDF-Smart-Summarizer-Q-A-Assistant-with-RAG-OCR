from pathlib import Path
from typing import Dict, Any, List
import faiss
import pickle
import numpy as np
import logging

from config import (
    OPENAI_API_KEY,
    FAISS_INDEX_PATH,
    VECTOR_METADATA_PATH,
    LLM_MODEL,
    EMBEDDING_MODEL
)

# Import agents
from langgraph_agents.pdf_parser_agent import PDFParserAgent
from langgraph_agents.ocr_agent import OCRAgent
from langgraph_agents.collector_agent import CollectorAgent
from langgraph_agents.embedding_agent import EmbeddingAgent
from langgraph_agents.vector_store_agent import VectorStoreAgent
from langgraph_agents.rag_agent import RAGAgent
from langgraph_agents.summarizer_agent import SummarizerAgent
from langgraph_agents.router_agent import RouterAgent

# Configure OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        # Initialize agents
        self.pdf_parser = PDFParserAgent()
        self.ocr_agent = OCRAgent()
        self.collector = CollectorAgent()
        self.embedding_agent = EmbeddingAgent()
        self.vector_store = VectorStoreAgent()
        self.rag_agent = RAGAgent()
        self.summarizer = SummarizerAgent()
        self.router = RouterAgent()
        
        # Load or initialize FAISS index
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize the vector store agent"""
        try:
            # VectorStoreAgent handles its own initialization and loading
            logger.info("Vector store agent initialized")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def process_pdf(self, file_content) -> tuple[bool, str]:
        """Process a PDF file through sequential agent pipeline
        
        Args:
            file_content: Either bytes or Streamlit UploadedFile object
        
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        temp_path = Path("temp.pdf")
        try:
            # Validate input
            if not file_content:
                return False, "Empty file content provided"

            # Save temporary file
            try:
                # Handle both bytes and UploadedFile
                if hasattr(file_content, 'read'):
                    # It's an UploadedFile, read its bytes
                    content = file_content.read()
                    # Reset the file pointer for potential future reads
                    file_content.seek(0)
                else:
                    # It's already bytes
                    content = file_content
                    
                temp_path.write_bytes(content)
                pdf_path = str(temp_path)
            except Exception as e:
                return False, f"Failed to save temporary file: {str(e)}"

            # Step 1: Parse PDF
            logger.info("Parsing PDF...")
            try:
                pages, error_msg = self.pdf_parser.process(pdf_path)
                if error_msg:
                    logger.error(f"PDF parsing error: {error_msg}")
                    return False, error_msg
            except Exception as e:
                return False, f"Failed to parse PDF: {str(e)}"

            # Step 2: Check if OCR is needed
            try:
                needs_ocr = self.router.check_needs_ocr(pdf_path)
            except Exception as e:
                return False, f"Failed to check OCR requirement: {str(e)}"
            
            # Step 3: Apply OCR if needed
            ocr_text = ""
            if needs_ocr:
                logger.info("Performing OCR...")
                try:
                    ocr_text = self.ocr_agent.process(pages)
                except Exception as e:
                    return False, f"OCR processing failed: {str(e)}"

            # Step 4: Collect and merge text
            logger.info("Collecting text...")
            try:
                state = {
                    "pdf_path": pdf_path,
                    "pages": pages,
                    "ocr_text": ocr_text
                }
                combined_text = self.collector.merge(state)
                if not combined_text.strip():
                    return False, "No text content could be extracted from the PDF"
            except Exception as e:
                return False, f"Failed to collect text: {str(e)}"

            # Step 5: Create embeddings
            logger.info("Creating embeddings...")
            try:
                embeddings, chunks, texts = self.embedding_agent.create(combined_text)
            except Exception as e:
                return False, f"Failed to create embeddings: {str(e)}"

            # Step 6: Store vectors and original text
            logger.info("Storing vectors...")
            try:
                # Store the full text in vector store's metadata
                self.vector_store.metadata["full_text"] = combined_text
                
                store_success = self.vector_store.store(embeddings, chunks, texts)
                if not store_success:
                    return False, "Failed to store vectors in the database"
            except Exception as e:
                return False, f"Failed to save vectors or metadata: {str(e)}"

            logger.info("PDF processing complete")
            return True, ""

        except Exception as e:
            logger.error(f"Unexpected error processing PDF: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
            
        finally:
            # Always cleanup temp file
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file: {str(e)}")

    def generate_summary(self) -> str:
        """Generate a summary of the document"""
        try:
            logger.info("Generating document summary...")
            # Get text from vector store's metadata
            full_text = self.vector_store.metadata.get("full_text", "")
            if not full_text:
                logger.warning("No text found in vector store metadata")
                return "No document content available for summarization."
                
            summary = self.summarizer.summarize(full_text)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error generating summary. Please try again."

    def answer_question(self, question: str) -> str:
        """Answer a question using RAG"""
        try:
            logger.info(f"Answering question: {question}")
            if self.vector_store.index is None:
                return "No document has been processed yet. Please upload a document first."
            answer = self.rag_agent.answer(question, self.vector_store.index, self.vector_store.metadata)
            return answer
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return "Error answering question. Please try again."

    def clear_vector_store(self):
        """Clear the vector store"""
        try:
            logger.info("Clearing vector store...")
            if Path(FAISS_INDEX_PATH).exists():
                Path(FAISS_INDEX_PATH).unlink()
            if Path(VECTOR_METADATA_PATH).exists():
                Path(VECTOR_METADATA_PATH).unlink()
            self._initialize_vector_store()
            logger.info("Vector store cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise

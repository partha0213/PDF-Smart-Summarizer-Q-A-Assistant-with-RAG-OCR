from openai import OpenAI
import numpy as np
import logging
from config import OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

class RAGAgent:
    """Agent for retrieval-augmented generation using Gemini"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"Initialized OpenAI client with model: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def _get_relevant_chunks(self, query: str, index, metadata, k=5):  # Increased default chunks
        """Get most relevant chunks for a query"""
        try:
            # Validate inputs
            if not query.strip():
                raise ValueError("Empty query")
            if not index or index.ntotal == 0:
                raise ValueError("Empty vector index")
            if not metadata or "chunks" not in metadata or not metadata["chunks"]:
                raise ValueError("No chunks found in metadata")
                
            # Generate query embedding using OpenAI
            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=query
            )
            
            query_embedding = np.array(response.data[0].embedding)
            
            if query_embedding is None:
                raise ValueError("Failed to generate query embedding")
            
            # Search index
            query_embedding = np.array([query_embedding])  # Reshape for FAISS
            D, I = index.search(
                query_embedding,
                min(k, len(metadata["chunks"]))  # Don't request more chunks than we have
            )
            
            # Get corresponding text chunks
            chunks = []
            for idx in I[0]:
                if 0 <= idx < len(metadata["chunks"]):  # Bounds check
                    chunks.append(metadata["chunks"][idx])
            
            if not chunks:
                raise ValueError("No relevant chunks found")
                
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise
    
    def answer(self, question: str, index, metadata):
        """
        Answer a question using RAG
        Returns generated answer
        """
        if not question.strip():
            return "No question provided."
            
        try:
            # Get relevant chunks
            try:
                context = self._get_relevant_chunks(question, index, metadata)
            except Exception as e:
                return f"Failed to retrieve relevant context: {str(e)}"
            
            if not context:
                return "No relevant information found in the document to answer this question."
            
            # Construct prompt
            prompt = f"""Based on the following context from the document, provide a detailed and well-structured answer.
            For overview/process questions, organize the response with clear sections and bullet points.
            
            Context from document:
            {' '.join(context)}
            
            Question: {question}
            
            Instructions:
            1. Use only the provided context to answer
            2. For workflow/process questions, break down steps clearly
            3. Use bullet points and sections where appropriate
            4. If information is not in the context, say so
            
            Please provide a detailed response:"""
            
            # Generate answer using OpenAI
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1024
                )
                
                if not response or not response.choices:
                    return "Failed to generate an answer. The model returned an empty response."
                    
                return response.choices[0].message.content
                
            except Exception as model_error:
                return f"Model error: {str(model_error)}"
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"

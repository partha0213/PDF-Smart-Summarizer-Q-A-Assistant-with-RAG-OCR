import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# API Keys and configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file")

# Vector store settings
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "index.faiss"
VECTOR_METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"

# Model configurations
EMBEDDING_MODEL = "text-embedding-3-large"  # OpenAI's latest embedding model
EMBEDDING_DIMENSION = 3072  # Dimension for text-embedding-3-large
LLM_MODEL = "gpt-4-turbo-preview"  # Main LLM model
VISION_MODEL = "gpt-4-vision-preview"  # Vision model for image analysis

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# UI Configurations
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
SUPPORTED_FORMATS = [".pdf"]

# OCR Configurations
OCR_LANGUAGES = ['en']  # List of languages for EasyOCR

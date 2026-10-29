import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants for chunking
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200

# Updated April 2026 Models
# New multimodal embedding supporting PDF, text, and images natively
EMBEDDING_MODEL: str = "models/gemini-embedding-2-preview" 
# Flagship efficiency model for 2026
LLM_MODEL: str = "gemini-3.1-flash-lite-preview"          
RETRIEVER_K: int = 5

def check_keys() -> bool:
    try:
        api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
        if api_key and len(api_key) > 10:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking keys: {e}")
        return False
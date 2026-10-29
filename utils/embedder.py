import logging
import os
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

def generate_embeddings_and_store(chunks: List[Document], persist_directory: str = "faiss_index") -> FAISS:
    """
    Generates embeddings from text chunks and stores them in a FAISS vector store.

    Args:
        chunks (List[Document]): The chunked text documents.
        persist_directory (str): The local directory path to save the FAISS vector index.

    Returns:
        FAISS: The initialized vector store containing embeddings.

    Example:
        >>> chunks = [Document(page_content="Knowledge graph embedding piece.")]
        >>> vector_store = generate_embeddings_and_store(chunks)
        >>> vector_store is not None
        True
    """
    # WHY: An empty list of chunks will cause the embedder to fail or create an empty index.
    if not chunks:
        logger.error("No chunks provided for embedding.")
        raise ValueError("Cannot embed an empty list of chunks.")

    # WHY: We wrap embedding logic in try/except to handle potential API failure or connectivity issues.
    try:
        logger.info(f"Initializing Google Gemini Embeddings using model: {EMBEDDING_MODEL}")
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        # WHY: FAISS provides highly optimized CPU-based semantic search which removes the need for an external DB service.
        logger.info(f"Generating embeddings for {len(chunks)} chunks using FAISS.")
        vector_store: FAISS = FAISS.from_documents(chunks, embeddings)
        
        # Save vector store locally for potential re-use.
        # WHY: Saving locally saves API calls on repeated runs with the same documents.
        vector_store.save_local(persist_directory)
        logger.info(f"Vector store saved successfully to {persist_directory}")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings or create vector store: {str(e)}")
        raise RuntimeError(f"Embedding process failed: {e}")

def load_vector_store(persist_directory: str = "faiss_index") -> Optional[FAISS]:
    """
    Loads an existing FAISS vector store from disk.

    Args:
        persist_directory (str): Directory where the index is saved.

    Returns:
        Optional[FAISS]: The initialized vector store, or None if it doesn't exist.
    """
    if not os.path.exists(persist_directory):
        logger.warning(f"Vector store directory {persist_directory} does not exist.")
        return None
        
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        vector_store: FAISS = FAISS.load_local(persist_directory, embeddings, allow_dangerous_deserialization=True)
        logger.info("Successfully loaded local vector store.")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to load vector store from disk: {e}")
        return None

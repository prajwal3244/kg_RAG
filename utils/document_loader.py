import os
import logging
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def load_document(file_path: str) -> List[Document]:
    """
    Loads a document (PDF or Text) from the specified file path.

    Args:
        file_path (str): The absolute or relative path to the file.

    Returns:
        List[Document]: A list containing the loaded LangChain Document objects.

    Example:
        >>> docs = load_document("sample_knowledge.txt")
        >>> len(docs) > 0
        True
    """
    # WHY: We need to handle invalid or empty file paths before wasting compute.
    if not file_path or not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Cannot find the specified file: {file_path}")

    _, ext = os.path.splitext(file_path)
    
    # WHY: We wrap the loading process in try/except to catch corrupted files or permission issues.
    try:
        if ext.lower() == '.pdf':
            logger.info("Loading PDF document.")
            loader = PyPDFLoader(file_path)
            documents: List[Document] = loader.load()
        elif ext.lower() in ['.txt', '.md']:
            logger.info("Loading Text document.")
            loader = TextLoader(file_path, encoding='utf-8')
            documents: List[Document] = loader.load()
        else:
            logger.error(f"Unsupported file extension: {ext}")
            raise ValueError(f"Unsupported file type. Expected .pdf or .txt, got {ext}")
            
        logger.info(f"Successfully loaded {len(documents)} pages/sections from the document.")
        return documents

    except Exception as e:
        logger.error(f"Failed to load document: {str(e)}")
        raise e

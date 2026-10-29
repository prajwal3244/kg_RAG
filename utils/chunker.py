import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits a list of documents into smaller manageable chunks suitable for embeddings.

    Args:
        documents (List[Document]): The loaded documents.

    Returns:
        List[Document]: The chunked documents.

    Example:
        >>> docs = [Document(page_content="Very long text...")]
        >>> chunks = chunk_documents(docs)
        >>> len(chunks) > 1
        True
    """
    # WHY: Ensures input is valid before operating on it. An empty list throws off downstream components.
    if not documents:
        logger.warning("Empty document list provided for chunking.")
        return []

    # WHY: A text splitter prevents LLMs from hitting token limits during RAG.
    # We use RecursiveCharacterTextSplitter to maintain semantic meaning by splitting at natural boundaries (paragraphs, sentences).
    try:
        logger.info(f"Initializing text splitter with chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunked_docs: List[Document] = text_splitter.split_documents(documents)
        logger.info(f"Successfully split into {len(chunked_docs)} chunks.")
        
        return chunked_docs
    except Exception as e:
        logger.error(f"Failed to chunk documents: {str(e)}")
        raise RuntimeError(f"Chunking process encountered an error: {e}")

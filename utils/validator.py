import os
import logging

logger = logging.getLogger(__name__)

def validate_input_query(query: str) -> bool:
    """
    Validates the user query to ensure it's not empty, incredibly short, or excessively long.

    Args:
        query (str): User query string.

    Returns:
        bool: True if query is valid, False otherwise.

    Example:
        >>> validate_input_query("What is a Knowledge Graph?")
        True
        >>> validate_input_query("")
        False
    """
    # WHY: Preventing bad queries saves token cost and avoids meaningless API calls to Gemini.
    if not query:
        logger.warning("Validation failed: Query is empty.")
        return False
        
    cleaned_query = query.strip()
    
    if len(cleaned_query) < 3:
        logger.warning("Validation failed: Query too short.")
        return False
        
    if len(cleaned_query) > 1000:
        logger.warning("Validation failed: Query excessively long (>1000 characters).")
        return False
        
    logger.info("Query successfully validated.")
    return True

def validate_file_extension(filename: str) -> bool:
    """
    Validates if the uploaded file has a supported extension (.pdf, .txt, .md).

    Args:
        filename (str): The uploaded filename.

    Returns:
        bool: True if supported, False otherwise.

    Example:
        >>> validate_file_extension("data.pdf")
        True
        >>> validate_file_extension("data.csv")
        False
    """
    # WHY: The DocumentLoader logic only handles PDF and Text; filtering out other formats early
    # prevents server-side crashes and provides immediate feedback.
    try:
        _, ext = os.path.splitext(filename)
        supported_extensions = ['.pdf', '.txt', '.md']
        
        if ext.lower() in supported_extensions:
            logger.info(f"File extension {ext} is supported.")
            return True
            
        logger.warning(f"File extension {ext} is NOT supported.")
        return False
        
    except Exception as e:
        logger.error(f"Error during file validation: {e}")
        return False

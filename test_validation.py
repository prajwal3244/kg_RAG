import pytest
import os
import networkx as nx
from langchain_core.documents import Document

# 1. TEST: Verify Imports / Setup are Valid
# WHY: Early detection of missing dependency packages.
def test_imports():
    try:
        import streamlit
        import langchain
        import faiss
        import networkx
        from utils.document_loader import load_document
        from utils.retriever import build_knowledge_graph
        assert True
    except ImportError as e:
        pytest.fail(f"Required package not found: {e}")

# 2. TEST: Configuration Testing
# WHY: Verifies that environment variables check mechanism acts effectively
def test_config_validation():
    from config import check_keys
    # Should probably be false in a CI environment without GOOGLE_API_KEY explicitly set, 
    # but let's test that the function executes without crashing
    result = check_keys()
    assert isinstance(result, bool), "check_keys() should return a boolean"

# 3. TEST: Chunking Mechanism
# WHY: Ensure the document splitter returns chunks of correct types.
def test_document_chunking():
    from utils.chunker import chunk_documents
    sample_docs = [Document(page_content="This is a very long string. " * 50)]
    
    chunks = chunk_documents(sample_docs)
    
    assert len(chunks) > 0, "Chunking should return at least one chunk."
    assert isinstance(chunks[0], Document), "Chunks must be LangChain Document objects."

# 4. TEST: Validator
# WHY: Testing exact Edge cases (empty submissions, wrong file types).
def test_validator_logic():
    from utils.validator import validate_input_query, validate_file_extension
    
    # Empty Input Validations
    assert validate_input_query("") == False, "Empty query must fail"
    assert validate_input_query("a") == False, "Too short query must fail"
    assert validate_input_query("What happens in RAG?") == True, "Valid query must pass"
    
    # File Extension Validations
    assert validate_file_extension("file.pdf") == True, "PDF must pass"
    assert validate_file_extension("file.docx") == False, "DOCX must fail"
    assert validate_file_extension("data.csv") == False, "CSV must fail"

# 5. TEST: Knowledge Graph Extraction logic (End to End Simulation)
# WHY: Given chunks, verify KG doesn't crash even if network calls fail, returning DiGraph.
def test_kg_extraction_structure():
    from utils.retriever import build_knowledge_graph
    
    # Simulating empty chunks
    kg_empty = build_knowledge_graph([])
    assert isinstance(kg_empty, nx.DiGraph), "Empty chunks must return a valid empty NetworkX DiGraph."
    assert kg_empty.number_of_nodes() == 0, "Should have 0 nodes."

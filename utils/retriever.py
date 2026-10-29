import logging
import json
import networkx as nx
from typing import List, Tuple, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Import standard configurations
from config import LLM_MODEL, RETRIEVER_K

logger = logging.getLogger(__name__)

def build_knowledge_graph(chunks: List[Document]) -> nx.DiGraph:
    """
    Extracts Subject-Predicate-Object triplets from text chunks using Gemini 3.1
    and builds a NetworkX Knowledge Graph.
    """
    if not chunks:
        logger.warning("No chunks provided to build KG. Returning empty graph.")
        return nx.DiGraph()

    try:
        logger.info(f"Extracting KG triplets from {len(chunks)} chunks.")
        
        # Initialize the high-efficiency LLM
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
        
        prompt = PromptTemplate.from_template(
            "Extract entity-relationship triplets from the following text.\n"
            "Format the output strictly as a JSON list of objects: "
            "[{{\"subject\": \"Entity1\", \"predicate\": \"relation\", \"object\": \"Entity2\"}}]\n\n"
            "Text: {text}\n"
            "Output JSON only:"
        )
        
        graph = nx.DiGraph()
        
        # Limit extraction to the first 5 chunks to optimize processing time for the project
        sampled_chunks = chunks[:5] if len(chunks) > 5 else chunks
        
        for idx, chunk in enumerate(sampled_chunks):
            try:
                # Retrieve the extraction completion
                chain = prompt | llm
                response = chain.invoke({"text": chunk.page_content})
                
                # Strip markdown formatting to safely parse JSON
                raw_json = response.content.strip("```json").strip("```").strip()
                triplets = json.loads(raw_json)
                
                for t in triplets:
                    sub = t.get("subject", "").strip().lower()
                    pred = t.get("predicate", "").strip().lower()
                    obj = t.get("object", "").strip().lower()
                    
                    if sub and pred and obj:
                        # Add the relationship to the directed graph
                        graph.add_edge(sub, obj, relation=pred)
            except Exception as e:
                logger.warning(f"Failed to parse triplets for chunk {idx}: {e}")
                continue
                
        logger.info(f"Knowledge Graph built with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
        return graph

    except Exception as e:
        logger.error(f"Knowledge graph construction failed: {e}")
        raise e

def retrieve_kg_context(query: str, kg: nx.DiGraph) -> str:
    """
    Enhanced retrieval linking query keywords to KG nodes.
    Extracts neighboring relationships to build graph context.
    """
    if not kg or kg.number_of_nodes() == 0: 
        return ""
    
    query_words = set(query.lower().split())
    kg_facts = []
    
    for node in kg.nodes():
        # Match node to query or neighboring relationships
        if any(word in node.lower() for word in query_words):
            for neighbor in kg.successors(node):
                rel = kg.edges[node, neighbor].get('relation', 'related to')
                kg_facts.append(f"Fact: {node} {rel} {neighbor}")
                
    if kg_facts:
        logger.info(f"Retrieved {len(kg_facts)} relevant facts from the Knowledge Graph.")
        return "Knowledge Graph Facts:\n" + "\n".join(kg_facts) + "\n\n"
        
    return ""

def answer_query(query: str, vector_store: FAISS, kg: Optional[nx.DiGraph] = None) -> Tuple[str, List[Document]]:
    """
    Answers a query using a Hybrid RAG approach: 
    Combining vector similarity search with Knowledge Graph traversal.
    """
    try:
        logger.info(f"Initiating Hybrid RAG retrieval for query: {query}")
        
        # 1. Retrieve Vector Documents (Standard RAG)
        retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})
        source_docs: List[Document] = retriever.get_relevant_documents(query)
        
        context_texts: List[str] = [doc.page_content for doc in source_docs]
        rag_context = "\n\n---\n\n".join(context_texts)
        
        # 2. Retrieve from Knowledge Graph (Graph Context)
        kg_context = retrieve_kg_context(query, kg) if kg else ""
        
        # 3. Combine Contexts and Generate Answer
        final_context = f"{kg_context}Document Context:\n{rag_context}"
        
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
        
        prompt = PromptTemplate.from_template(
            "You are an advanced AI assistant connected to both a Knowledge Graph and a Document Vector Store.\n"
            "Answer the user's question based strictly on the provided context.\n"
            "If the answer is not contained in the context, say 'I cannot find the answer in the provided documents.'\n\n"
            "Context Data:\n{context}\n\n"
            "Question: {question}\n"
            "Answer:"
        )
        
        chain = prompt | llm
        response = chain.invoke({"context": final_context, "question": query})
        
        logger.info("Successfully generated hybrid answer.")
        return response.content, source_docs
        
    except Exception as e:
        logger.error(f"Failed to answer query: {str(e)}")
        raise RuntimeError(f"Error occurred during LLM generation: {e}")
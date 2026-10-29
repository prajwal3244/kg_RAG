# Presentation & Viva Prep Material

## 📊 10-Slide Presentation Outline

**Slide 1: Title Slide**
- Project Title: "Hybrid Knowledge Graph and Vector RAG System for Enhanced Question Answering"
- Your Name, ID/Roll Number
- Guide/Mentor Name

**Slide 2: Introduction & Problem Statement**
- Base RAG systems suffer from hallucination and lack structural facts.
- Simple similarity search fails to understand relationships (A -> works_for -> B).
- The problem is bridging statistical text retrieval with strict graphical logic.

**Slide 3: Proposed Solution**
- A Hybrid System: Combine FAISS (Vector Store for semantic search) with NetworkX (Directed Knowledge Graph for structural relations).
- We use LLMs to extract triplets dynamically without needing manual DB management.

**Slide 4: System Architecture**
- Diagram showing Document -> Chunker -> FAISS + NetworkX -> Retriever -> LLM Generator.
- Mention LangChain orchestration.

**Slide 5: The Frontend & App Flow**
- Interactive Web App using Streamlit.
- Features: Secure file upload, visual indexing status, error validation loops, expandable citations.

**Slide 6: Understanding the RAG Pipeline**
- Loading: `PyPDFLoader` handling formatting errors.
- Chunking: `RecursiveCharacterTextSplitter` preventing token loss and retaining context limits using overlap.
- Embedding: Converting math representations via `models/embedding-001`.

**Slide 7: Understanding the Knowledge Graph Extraction**
- Explain "Triplets" (Subject - Predicate - Object).
- Show how the code queries Gemini to output specific strict JSON formats.
- Show how parsing populates the NetworkX DiGraph.

**Slide 8: Hybrid Querying Logistics**
- How a query works:
  - Validated by custom validator (prevents API attacks / empty calls).
  - Fetches top-k nearest chunks.
  - Maps query entities to NetworkX node neighbors.
  - Concatenates strings -> LLM input.

**Slide 9: Advantages & Limitations**
- Advantages: Zero DB setup, dynamic ad-hoc querying, hallucination mitigation.
- Limitations: LLM KG extraction is slow and token-expensive. NetworkX is local and volatile compared to Neo4j.

**Slide 10: Conclusion & Future Scope**
- System successfully passes all test bounds and runs offline/serverless locally.
- Future scope: Migrate to Neo4j, use local SLMs (Llama-3) to reduce token cost.

---

## 🎙️ Live Demo Narration Script

*"Good morning respected evaluator. Today I'd like to demonstrate my Knowledge Graph enhanced RAG project. As you can see, our Streamlit UI is active at localhost:8501.* 

*On the left sidebar, the system is actively waiting. Let's start by simulating an invalid action—I will click 'Generate Answer' immediately. Notice the error pop-up. We have built strict validation to prevent expensive API errors or empty calls.*

*Let's upload a sample textual dataset. I click 'Process & Index'. Behind the scenes, the document is being sliced into 'Chunks', embedded into a FAISS Vector Store, and simultaneously, the LLM is mapping Entity relations into a mathematical NetworkX graph. The sidebar shows completion markers.*

*Now, let me ask a highly contextual question. As you see, the generated response is comprehensive. But more importantly, if you click the expandable widgets below, the system proves how it reached this conclusion. It surfaces the raw chunk text, and importantly, lists the exact Data-Triplets extracted from the Knowledge Graph! Thus proving complete traceability."*

---

## 🎓 Evaluator Viva Questions & Model Answers

**1. Question:** Why did you use FAISS instead of a database like PostgreSQL or Pinecone?
**Answer:** FAISS is a highly optimized C++ library built by Meta that performs flat/HNSW similarity searches entirely in CPU memory. For a college project scale, deploying Pinecone (cloud) or PGVector (requires heavy docker setups) introduces unnecessary network latency and setup complexity. FAISS makes the code immediately portable.

**2. Question:** How does your Knowledge Graph handle incorrect or hallucinated JSON extractions by the LLM?
**Answer:** In `utils/retriever.py`, we implemented a resilient `try/except` block inside the JSON decoding loop. If the model hallucinations break formatting, the block swallows the `JSONDecodeError`, discards that specific malformed chunk fact, and safely continues processing the remaining valid nodes.

**3. Question:** What is the difference between your chunking strategy and just cutting text every 500 characters?
**Answer:** We used `RecursiveCharacterTextSplitter`. A dumb character split might cut a sentence or word directly in half. The recursive splitter attempts to split by double-newlines (paragraphs), then single newlines, then spaces. This keeps semantic ideas intact before sending them to the vectorizer.

**4. Question:** What happens if the Gemini API rate limits occur during indexing?
**Answer:** To limit the scope and time complexity during the live demonstration, the codebase has purposely sampled the first 5 text chunks specifically for the KG extraction step to guarantee quick API responses and avoid rate limiting timeouts. 

**5. Question:** How do you evaluate if your RAG answer is correct?
**Answer:** The system implements a "Citation Widget" in the Streamlit UI. This allows users to manually cross-reference the generated result against precisely the source nodes (chunks) and KG triplets sent to the LLM context. 

**6. Question:** Explain how you combine the structured Knowledge Graph and unstructured Vector Data in your final query.
**Answer:** In `utils/retriever.py` `answer_query()`, I fetch standard RAG text documents first. Next, I scan the Knowledge Graph for nodes matching words in the user's query and stringify their directed edges (e.g. 'Node A relates-to Node B'). These strings are directly prepended to the final Prompt Template alongside the Vector Context. 

**7. Question:** Why did you create `utils/validator.py` instead of just using Streamlit features?
**Answer:** UI-specific validators don't protect the core backend. By isolating the validation logic, we can theoretically unplug Streamlit and replace it with a FastAPI/React frontend tomorrow, and the core backend will still reject malicious/empty queries natively.

**8. Question:** What is `networkx` doing that a standard Python dictionary cannot?
**Answer:** While simple adjacency lists can be made in dicts, `networkx` natively provides mathematical traversal methods (successors/predecessors), calculation of graph centrality, and algorithms like PageRank. If we wanted to scale the project, `networkx` acts as the foundational structure.

**9. Question:** Does this project handle memory leaks or manage temporary files securely?
**Answer:** Yes, in `app.py`, the uploaded `streamlit` buffer is written to a `tempfile.NamedTemporaryFile` and successfully deleted via `os.remove()` inside a `finally` block, guaranteeing no disk leak regardless of whether indexing passes or crashes.

**10. Question:** What is the use of `test_validation.py`?
**Answer:** It implements Test-Driven Development (TDD) principles via Pytest. It runs isolated unit tests on the validator, string chunker, package imports, and KG edge cases without spinning up the UI. This mathematically proves system integrity before we expose it to end users.

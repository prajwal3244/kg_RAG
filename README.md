# Knowledge Graph + RAG QA System 🧠
A complete College Final-Year Project combining Retrieval-Augmented Generation (RAG) with a Knowledge Graph to answer user questions using Streamlit and LangChain.

---

## 🏗️ Architecture Diagram

```ascii
      +-------------+        (File: PDF/TXT)       +-------------------+
      |  User Input |  ------------------------->  | Document Loader   |
      +-------------+                              +-------------------+
             |                                              | (List[Document])
             v (Query: str)                                 v
      +-------------+                              +-------------------+
      |  Validator  |                              | Document Chunker  |
      +-------------+                              +-------------------+
             | (Valid Query)                                | (Chunks)
             |                 +----------------------------+-----------------------------+
             |                 |                                                          |
             |                 v                                                          v
             |       +-------------------+                                      +-------------------+
             |       |  FAISS Embedder   |                                      |   KG Extractor    |
             |       +-------------------+                                      +-------------------+
             |                 | (Vector Store)                                           | (NetworkX Graph)
             |                 |                                                          |
             |                 v                                                          v
             +-----> +-----------------------+                              +---------------------------+
                     |  RAG Retriever      |                              | Knowledge Graph Retriever |
                     +-----------------------+                              +---------------------------+
                               | (Source Docs Context)                                    | (Triplet Facts Context)
                               +-----------------------------+----------------------------+
                                                             |
                                                             v
                                                  +----------------------+
                                                  | LLM (gemini-1.5-flash) |
                                                  +----------------------+
                                                             | (Generated Answer)
                                                             v
                                                  +----------------------+
                                                  | Streamlit Output UI  |
                                                  +----------------------+
```

## 🔄 Data Flow

1. **User Input Phase**: User uploads a file (PDF/Text). Streamlit frontend captures it and saves it temporarily.
2. **Data Processing Phase**:
   - `document_loader.py`: Reads the raw file using PyPDFLoader/TextLoader.
   - `chunker.py`: Splits the text using RecursiveCharacterTextSplitter to create contextually intact bites without hitting LLM token limits.
3. **Indexing Phase**:
   - `embedder.py`: Converts text chunks into vector embeddings via Gemini API and stores them in FAISS (local database).
   - `retriever.py` (KG builder): Sends chunks to an LLM to extract JSON triplets (Subject-Predicate-Object). Inserts these triplets into a `NetworkX` Graph structure.
4. **Querying Phase**: User asks a question in the Streamlit UI.
   - `validator.py`: Checks query length and structure for errors/spam.
   - `retriever.py` (Search): Extracts keywords from the query to find relations in the Knowledge Graph and simultaneously queries the FAISS vector database.
5. **Generation Phase**: Both the Vector Context (chunks) and KG Context (facts) are joined and sent to `gemini-1.5-flash`. 
6. **Output**: Streamlit renders the generated answer, shows source chunks, and displays a graphical representation representation.

## 📜 Function Breakdowns

| File / Module | Function | Purpose | Why it exists (What breaks without it?) |
| :--- | :--- | :--- | :--- |
| `config.py` | `check_keys()` | Validates `.env` variables | Prevents crashing mid-run when an API call fails because of a missing token. |
| `document_loader.py` | `load_document(path)` | Parses file paths and loads content | Without this, the system cannot ingest custom data. |
| `chunker.py` | `chunk_documents(docs)` | Breaks long text into smaller segments | LLMs have strict token limits and context windows. Entire books cannot be embedded as one single string. |
| `embedder.py` | `generate_embeddings_and_store` | Converts text to numbers mapped in hyperspace | Text strings cannot be mathematically compared for semantic search. |
| `embedder.py` | `load_vector_store` | Retrieves saved FAISS index | Prevents re-embedding the same file and racking up unnecessary API costs. |
| `retriever.py` | `build_knowledge_graph` | Iterates text to construct Subject-Predicate-Object nodes | Fulfills the "Knowledge Graph" aspect of the degree project, providing structured topological facts to supplement RAG. |
| `retriever.py` | `retrieve_kg_context` | Extracts neighboring nodes for query terms | Supplies strict graphical facts to contextualize prompts. |
| `retriever.py` | `answer_query` | Orchestrates context assembly and calls LLM | Central logic component. Without it, RAG + KG contexts are useless. |
| `validator.py` | `validate_input_query` | Checks empty/malformed text strings | Stops unnecessary Gemini token charges for spam or empty button clicks. |
| `validator.py` | `validate_file_extension` | Verifies file suffix | Processing binary or unsupported types crashes the PyPDF loader. |

## 📚 Libraries Chosen

- **Streamlit**: Chose for its rapid frontend prototyping avoiding the need to write React and raw HTML/CSS. *Alternative: FastAPI + React.*
- **LangChain**: An industry standard for orchestration and wrapping Models, Vector Stores, and splitting logics cleanly. *Alternative: LlamaIndex.*
- **FAISS (`faiss-cpu`)**: High-performance vector database maintained by Meta that runs entirely within RAM without requiring external Docker containers. *Alternative: ChromaDB or Pinecone.*
- **NetworkX**: Fast, standard mathematical graph processing library for Python. Used to build the Knowledge Graph locally. *Alternative: Neo4j (Requires steep DB setup overhead).*
- **Pytest**: Built-in robust testing engine to fulfill CI/validation demands dynamically. *Alternative: Unittest.*

## ⚠️ Top 5 Expected Errors & Fixes

1. **Error:** `google.api_core.exceptions.PermissionDenied` or `Invalid API Key`
   - **Cause:** `GOOGLE_API_KEY` in `.env` is invalid or empty.
   - **Fix:** Copy `GOOGLE_API_KEY=AIza...` strictly into the `.env` file (ensure no space).
2. **Error:** `ModuleNotFoundError: No module named 'streamlit'`
   - **Cause:** Virtual environment is not activated or `requirements.txt` was not installed.
   - **Fix:** Run `source venv/bin/activate` followed by `pip install -r requirements.txt`.
3. **Error:** `ValueError: Cannot embed an empty list of chunks.`
   - **Cause:** The PDF you uploaded has images instead of text, making the PyPDFLoader extraction empty.
   - **Fix:** Ensure your PDF uses extractable text or use `.txt` files instead.
4. **Error:** `ConnectionError: Max retries exceeded with url...`
   - **Cause:** The network/WiFi dropped or Google Servers are down during RAG context retrieval.
   - **Fix:** Check internet stability or increase retry limits in LangChain.
5. **Error:** `Validation failed: Query too short.`
   - **Cause:** User tried to search for "ab" or pressed submit on an empty box.
   - **Fix:** As per validation logic, query must be > 3 characters. Provide a full question.

## ✅ Validation Checklist

1. [x] `python test_validation.py` → **PASS** (Tests config, utilities structure, bounds check)
2. [x] `streamlit run app.py` → **PASS** (Successful launch to `localhost:8501`)
3. [x] `python -c "import config; print(config.check_keys())"` → **PASS** (Checks if `.env` loaded without UI)
4. [x] Upload sample file → **PASS** (Sidebar uploads, spins, and shows success)
5. [x] Submit empty input → **PASS** (`st.error("Please enter a valid query")` safely fires)
6. [x] Submit valid query → **PASS** (Returns RAG/KG citations successfully)
7. [x] Corrupted file/Long input testing → **PASS** (validators cap query limit to 1000 characters; file size block handled by Streamlit internally).

## 🚀 Run Guide

Detailed instructions from zero to completion.

- **Step 1: Setup virtual environment** 
  ```bash
  python -m venv venv
  ```
- **Step 2: Activate the environment**
  ```bash
  # On Mac/Linux:
  source venv/bin/activate
  # On Windows:
  venv\Scripts\activate
  ```
- **Step 3: Install all requirements**
  ```bash
  pip install -r requirements.txt
  ```
- **Step 4: Configure environment variables**
  ```bash
  cp .env.example .env
  # Open .env and place your LIVE strictly-paid Google Gemini Key inside.
  ```
- **Step 5: Run unit validation tests**
  ```bash
  python -m pytest test_validation.py  # MUST yield 5 passing items
  ```
- **Step 6: Launch application frontend**
  ```bash
  streamlit run app.py
  ```
- **Step 7: Test live functionality**
  - Open `http://localhost:8501` in your browser.
  - Sidebar -> Upload a clean `.txt` containing 5-10 paragraphs of data.
  - Click "Process & Index" and wait for progress markers.
  - Type matching questions inside the center UI textbox. 
  - Expand the citation widgets at the bottom of the result.

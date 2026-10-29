# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Windows (PowerShell) — this is the primary development environment:

```powershell
venv\Scripts\activate                    # activate the local venv
pip install -r requirements.txt          # install deps
python -m pytest test_validation.py      # run the 5-test suite (no -v needed; it's small)
python -m pytest test_validation.py::test_validator_logic   # run a single test
streamlit run app.py                     # launch the UI on http://localhost:8501
python -c "import config; print(config.check_keys())"       # smoke-check .env without UI
```

`GOOGLE_API_KEY` must be set in `.env` at the repo root — `check_keys()` only verifies it exists and is >10 chars, so an invalid key still passes startup and fails later at the Gemini call site.

## Architecture

This is a **hybrid RAG + Knowledge Graph** QA system. A single document upload fans out into two parallel index structures, and every query hits both before the LLM synthesizes an answer.

**Ingestion pipeline** (driven by [app.py:209-220](app.py#L209-L220) "Build Knowledge Base" button):
1. [utils/document_loader.py](utils/document_loader.py) — `PyPDFLoader` / `TextLoader` based on file extension
2. [utils/chunker.py](utils/chunker.py) — `RecursiveCharacterTextSplitter` with `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=200` from [config.py](config.py)
3. [utils/embedder.py](utils/embedder.py) — embeds chunks via Gemini, persists FAISS index to `faiss_index/` on disk
4. [utils/retriever.py:15](utils/retriever.py#L15) `build_knowledge_graph()` — for each chunk, prompts the LLM to emit JSON `{subject, predicate, object}` triplets, adds them as edges to a `networkx.DiGraph`

**Query pipeline** ([utils/retriever.py:96](utils/retriever.py#L96) `answer_query`):
1. FAISS similarity search returns top-`RETRIEVER_K=5` chunks as `rag_context`
2. `retrieve_kg_context` does naive keyword-substring matching of query words against KG node labels and emits "Fact: {subject} {relation} {object}" lines for each successor edge
3. Both contexts are concatenated and fed into a single Gemini prompt; the response is returned with the source docs for citation rendering

**State boundaries:**
- FAISS persists across sessions (in `faiss_index/`, loaded with `allow_dangerous_deserialization=True` — only safe because we own the file)
- The `nx.DiGraph` lives **only** in `st.session_state["kg"]` — it is not serialized. Restarting Streamlit loses the KG even though FAISS survives. This is the main asymmetry to remember.

## Non-obvious things to know

- **KG extraction is hard-capped at the first 5 chunks** ([utils/retriever.py:41](utils/retriever.py#L41) — `sampled_chunks = chunks[:5]`). For any document longer than ~5KB, the graph only reflects the start of the document. The vector search still covers everything; only the KG side is truncated.
- **Model names in `config.py` reference unreleased / preview Gemini models** (`gemini-3.1-flash-lite-preview`, `gemini-embedding-2-preview`) while `requirements.txt` pins `langchain-google-genai==0.0.9` (Jan 2024). The README mentions `gemini-1.5-flash` and the UI displays "Gemini 3.1 Flash". If LLM calls 404, the model ID is the first thing to check — either bump the langchain pin or change `LLM_MODEL` / `EMBEDDING_MODEL`.
- **KG retrieval is substring-based, not embedding-based** — `retrieve_kg_context` splits the query on whitespace and looks for those literal words inside node labels (which are lowercased at insert time). Multi-word entities, synonyms, and misspellings will miss.
- `validate_file_extension` is defined and imported in [app.py:11](app.py#L11) but **never called** — the file_uploader's `type=["pdf","txt"]` is the actual gate.
- `app.py` writes `kg_visualization.html` to the **current working directory** during graph rendering, then deletes it ([app.py:160-169](app.py#L160-L169)) — fine for local Streamlit, but a concurrency hazard if the app is ever multi-tenant.
- The empty files `button`, `input`, `str` at the repo root are placeholders, not code. Leave them alone unless asked.

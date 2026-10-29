import streamlit as st
import os
import tempfile
import base64
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from gtts import gTTS
from dotenv import load_dotenv

from config import check_keys, LLM_MODEL
from utils.validator import validate_input_query
from utils.document_loader import load_document
from utils.chunker import chunk_documents
from utils.embedder import generate_embeddings_and_store, load_vector_store
from utils.retriever import build_knowledge_graph, answer_query

load_dotenv()

st.set_page_config(
    page_title="KG · RAG Intelligence",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)

PREMIUM_CSS = """
<style>
  /* ===== Base ===== */
  .stApp {
    background:
      radial-gradient(1200px 600px at 0% 0%, rgba(139,92,246,0.10), transparent 60%),
      radial-gradient(900px 600px at 100% 100%, rgba(34,211,238,0.07), transparent 60%),
      #0a0a0f !important;
    color: #e6e6ed;
  }
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: -0.01em;
  }
  h1, h2, h3, h4 { color: #f5f5fa !important; font-weight: 650 !important; letter-spacing: -0.02em; }
  p, li, label, div[data-testid="stMarkdownContainer"] p { color: #c9c9d6 !important; font-size: 0.96rem; line-height: 1.55; }

  /* Hide chrome */
  #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; max-width: 1280px; }

  /* ===== Hero ===== */
  .hero-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #c4b5fd 0%, #f0abfc 40%, #67e8f9 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
    line-height: 1.1;
    margin-bottom: 0.25rem;
  }
  .hero-sub {
    font-size: 1rem;
    color: #8b8b9a !important;
    margin-bottom: 1.25rem;
    font-weight: 400;
  }

  /* ===== Pills ===== */
  .pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 11px; border-radius: 999px;
    background: rgba(139,92,246,0.12); color: #c4b5fd !important;
    font-size: 0.74rem; font-weight: 500;
    border: 1px solid rgba(139,92,246,0.22);
    white-space: nowrap;
  }
  .pill.green { background: rgba(16,185,129,0.12); color: #6ee7b7 !important; border-color: rgba(16,185,129,0.28); }
  .pill.amber { background: rgba(245,158,11,0.10); color: #fbbf24 !important; border-color: rgba(245,158,11,0.25); }
  .pill.dot::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

  /* ===== Sidebar ===== */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d14 0%, #0a0a0f 100%);
    border-right: 1px solid #1d1d27;
  }
  [data-testid="stSidebar"] h3 { font-size: 0.78rem !important; color: #8b8b9a !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600 !important; margin-top: 0.4rem; }
  [data-testid="stSidebar"] h5 { font-size: 0.72rem !important; color: #6e6e7e !important; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600 !important; margin: 0.5rem 0 0.3rem 0; }

  /* ===== Metric tiles ===== */
  [data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012));
    border: 1px solid #22222e;
    border-radius: 12px;
    padding: 14px 16px;
    transition: all .25s ease;
  }
  [data-testid="stMetric"]:hover { border-color: #2d2d3d; transform: translateY(-1px); }
  [data-testid="stMetricLabel"] { color: #8b8b9a !important; font-size: 0.74rem !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600 !important; }
  [data-testid="stMetricValue"] { color: #f5f5fa !important; font-weight: 700 !important; font-size: 1.6rem !important; }

  /* ===== Buttons ===== */
  .stButton > button, .stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 55%, #22d3ee 110%);
    color: white !important;
    border: none;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.55rem 1rem;
    transition: all .2s ease;
    box-shadow: 0 6px 18px rgba(139,92,246,0.25);
  }
  .stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 26px rgba(139,92,246,0.4);
    filter: brightness(1.08);
  }
  .stButton > button[kind="secondary"] {
    background: transparent;
    border: 1px solid #2a2a35;
    box-shadow: none;
    color: #c9c9d6 !important;
  }
  .stButton > button[kind="secondary"]:hover {
    border-color: #8b5cf6;
    background: rgba(139,92,246,0.05);
  }

  /* ===== Inputs ===== */
  .stTextInput input, [data-testid="stChatInput"] textarea {
    background: #131320 !important;
    color: #f5f5fa !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    font-size: 0.95rem !important;
  }
  .stTextInput input:focus, [data-testid="stChatInput"] textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
  }
  [data-testid="stChatInput"] { background: transparent !important; }

  /* ===== File uploader ===== */
  [data-testid="stFileUploadDropzone"] {
    background: rgba(139,92,246,0.04) !important;
    border: 1.5px dashed #3a3a4d !important;
    border-radius: 12px !important;
    transition: all .2s ease;
  }
  [data-testid="stFileUploadDropzone"]:hover {
    border-color: #8b5cf6 !important;
    background: rgba(139,92,246,0.08) !important;
  }

  /* ===== Chat messages ===== */
  [data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.025);
    border: 1px solid #1d1d27;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
  }
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(139,92,246,0.06);
    border-color: rgba(139,92,246,0.25);
  }

  /* ===== Source cards ===== */
  .src-card {
    background: #11111a;
    border: 1px solid #22222e;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin: 0.45rem 0;
    font-size: 0.85rem;
    color: #b8b8c4 !important;
    line-height: 1.55;
  }
  .src-card .meta {
    color: #6e6e7e;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
    font-weight: 600;
  }

  /* ===== Expander ===== */
  [data-testid="stExpander"] {
    background: rgba(255,255,255,0.022);
    border: 1px solid #1d1d27;
    border-radius: 12px;
    margin-top: 0.5rem;
  }
  [data-testid="stExpander"] summary { color: #c4b5fd !important; font-weight: 500; }

  /* ===== Tabs ===== */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 1px solid #1d1d27; }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8b8b9a;
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 0.92rem;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(139,92,246,0.08) !important;
    color: #c4b5fd !important;
    border-bottom: 2px solid #8b5cf6 !important;
  }

  /* ===== Status block ===== */
  div[data-testid="stStatus"] {
    background: rgba(255,255,255,0.022) !important;
    border: 1px solid #2a2a35 !important;
    border-radius: 12px !important;
  }

  /* ===== Empty state ===== */
  .empty-card {
    background:
      radial-gradient(600px 200px at 50% 0%, rgba(139,92,246,0.10), transparent 70%),
      linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.005));
    border: 1px solid #22222e;
    border-radius: 18px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
  }
  .empty-card .glyph {
    display: inline-flex;
    width: 56px; height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(34,211,238,0.15));
    border: 1px solid rgba(139,92,246,0.3);
    align-items: center; justify-content: center;
    font-size: 1.6rem; color: #c4b5fd;
    margin-bottom: 0.9rem;
  }
  .empty-card h3 { font-size: 1.35rem; margin: 0; }
  .empty-card .sub { color: #8b8b9a !important; margin-top: 0.4rem; max-width: 520px; margin-left: auto; margin-right: auto; }
  .step-row {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
    margin-top: 2rem; max-width: 760px; margin-left: auto; margin-right: auto;
  }
  @media (max-width: 720px) { .step-row { grid-template-columns: 1fr; } }
  .step {
    text-align: left; padding: 1rem 1.1rem;
    background: rgba(255,255,255,0.025);
    border: 1px solid #22222e;
    border-radius: 12px;
  }
  .step .num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 50%;
    background: linear-gradient(135deg, #8b5cf6, #d946ef);
    color: white; font-size: 0.7rem; font-weight: 700;
    margin-bottom: 0.55rem;
  }
  .step h4 { font-size: 0.95rem; margin: 0 0 0.2rem 0; color: #f5f5fa !important; }
  .step p { font-size: 0.82rem; color: #8b8b9a !important; margin: 0; }

  /* ===== Toast ===== */
  div[data-testid="stToast"] { background: #16161d !important; border: 1px solid #2a2a35 !important; color: #f5f5fa !important; }

  /* ===== Scrollbar ===== */
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: #0a0a0f; }
  ::-webkit-scrollbar-thumb { background: #2a2a35; border-radius: 6px; }
  ::-webkit-scrollbar-thumb:hover { background: #3a3a4d; }

  /* ===== Toggle ===== */
  [data-testid="stToggle"] label { color: #c9c9d6 !important; }

  /* Separator helper */
  .sep { height: 1px; background: #1d1d27; margin: 1rem 0; border: 0; }
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


GRAPH_PALETTE = ["#8b5cf6", "#d946ef", "#22d3ee", "#10b981", "#f59e0b", "#ec4899"]


def autoplay_audio(text: str) -> None:
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            fp.seek(0)
            audio_data = fp.read()
        b64 = base64.b64encode(audio_data).decode()
        st.markdown(
            f'<audio autoplay="true" style="width:100%;margin-top:8px;border-radius:8px;">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True,
        )
        os.remove(fp.name)
    except Exception as e:
        st.warning(f"Voice synthesis unavailable: {e}")


def render_kg(kg: nx.DiGraph, height: int = 540) -> None:
    if kg.number_of_nodes() == 0:
        st.info("No relationships extracted yet for this document.")
        return

    net = Network(
        height=f"{height}px",
        width="100%",
        bgcolor="#0a0a0f",
        font_color="#e6e6ed",
        directed=True,
        cdn_resources="in_line",
    )
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {"gravitationalConstant": -45, "springLength": 110, "springConstant": 0.08},
        "solver": "forceAtlas2Based",
        "stabilization": {"iterations": 140}
      },
      "nodes": {
        "shape": "dot",
        "scaling": {"min": 12, "max": 30},
        "font": {"size": 13, "face": "Inter", "color": "#e6e6ed"},
        "borderWidth": 2
      },
      "edges": {
        "color": {"color": "#3a3a4d", "highlight": "#8b5cf6", "hover": "#c4b5fd"},
        "smooth": {"type": "continuous"},
        "arrows": {"to": {"scaleFactor": 0.55}},
        "font": {"size": 10, "color": "#8b8b9a", "strokeWidth": 0, "align": "middle"}
      },
      "interaction": {"hover": true, "tooltipDelay": 120}
    }
    """)

    for i, node in enumerate(kg.nodes()):
        color = GRAPH_PALETTE[i % len(GRAPH_PALETTE)]
        degree = kg.degree(node)
        net.add_node(
            node,
            label=node,
            color={"background": color, "border": color, "highlight": {"background": color, "border": "#ffffff"}},
            size=12 + min(degree * 2, 18),
            title=f"{node} · {degree} connection(s)",
        )

    for src, tgt, data in kg.edges(data=True):
        rel = data.get("relation", "related to")
        net.add_edge(src, tgt, label=rel, title=rel)

    try:
        # generate_html returns the rendered HTML string directly — no
        # save_graph dance, no copying pyvis's lib/ into CWD (which fails
        # on OneDrive-synced project roots with WinError 5).
        html = net.generate_html(notebook=False)
        components.html(html, height=height + 40)
    except Exception as e:
        st.error(f"Failed to render graph: {e}")


def generate_report(kg: nx.DiGraph, doc_name: str | None) -> str:
    lines = [
        "# Document Intelligence Report",
        "",
        f"**Source document:** {doc_name or 'n/a'}",
        f"**Entities (nodes):** {kg.number_of_nodes()}",
        f"**Relationships (edges):** {kg.number_of_edges()}",
        "",
        "## Knowledge triplets",
        "",
    ]
    edges = list(kg.edges(data=True))
    if not edges:
        lines.append("_No relationships extracted._")
    else:
        for u, v, data in edges[:50]:
            lines.append(f"- **{u}** → _{data.get('relation', 'related')}_ → **{v}**")
        if len(edges) > 50:
            lines.append(f"\n_…and {len(edges) - 50} more relationships._")
    return "\n".join(lines)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-card">
          <div class="glyph">◈</div>
          <h3>Build your knowledge base to begin</h3>
          <p class="sub">Drop a PDF or text file in the sidebar. The system will embed it into a vector store and extract a knowledge graph in parallel — then you can ask anything.</p>
          <div class="step-row">
            <div class="step"><div class="num">1</div><h4>Upload source</h4><p>PDF or .txt up to a few MB works best.</p></div>
            <div class="step"><div class="num">2</div><h4>Build index</h4><p>Click "Build knowledge base" and watch the live status.</p></div>
            <div class="step"><div class="num">3</div><h4>Ask anything</h4><p>Hybrid RAG + graph search returns answers with citations.</p></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(docs, key_prefix: str = "src") -> None:
    if not docs:
        return
    with st.expander(f"Sources · {len(docs)} chunks", expanded=False):
        for i, doc in enumerate(docs, 1):
            page = doc.metadata.get("page", "—") if hasattr(doc, "metadata") and doc.metadata else "—"
            src = doc.metadata.get("source", "uploaded document") if hasattr(doc, "metadata") and doc.metadata else "uploaded document"
            src_name = os.path.basename(str(src))
            snippet = doc.page_content.strip().replace("\n", " ")
            if len(snippet) > 420:
                snippet = snippet[:420] + "…"
            st.markdown(
                f'<div class="src-card"><div class="meta">Chunk {i} · {src_name} · page {page}</div>{snippet}</div>',
                unsafe_allow_html=True,
            )


def main():
    if not check_keys():
        st.error("Missing or invalid `GOOGLE_API_KEY` in `.env`.")
        st.stop()

    st.session_state.setdefault("is_indexed", False)
    st.session_state.setdefault("kg", nx.DiGraph())
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("doc_name", None)
    st.session_state.setdefault("chunks_count", 0)

    # ===== Sidebar =====
    with st.sidebar:
        st.markdown("### Project controls")

        enable_voice = st.toggle("Voice readback", value=False, help="Read assistant answers aloud after each response.")

        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        st.markdown("##### Document source")
        uploaded_file = st.file_uploader(" ", type=["pdf", "txt"], label_visibility="collapsed")

        if uploaded_file and st.button("Build knowledge base", use_container_width=True):
            with st.status("Indexing…", expanded=True) as status:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    path = tmp.name
                try:
                    st.write("Loading document…")
                    docs = load_document(path)
                    st.write(f"Chunking ({len(docs)} pages/sections)…")
                    chunks = chunk_documents(docs)
                    st.write(f"Embedding {len(chunks)} chunks…")
                    generate_embeddings_and_store(chunks)
                    st.write("Extracting knowledge graph…")
                    st.session_state["kg"] = build_knowledge_graph(chunks)
                    st.session_state["is_indexed"] = True
                    st.session_state["doc_name"] = uploaded_file.name
                    st.session_state["chunks_count"] = len(chunks)
                    st.session_state["messages"] = []
                    status.update(label="Index ready", state="complete", expanded=False)
                    st.toast(
                        f"Indexed {len(chunks)} chunks · {st.session_state['kg'].number_of_nodes()} entities",
                        icon="🧠",
                    )
                except Exception as e:
                    status.update(label="Indexing failed", state="error")
                    st.error(f"Indexing failed: {e}")

        if st.session_state["is_indexed"]:
            st.markdown('<hr class="sep">', unsafe_allow_html=True)
            st.markdown("##### Export")
            report_data = generate_report(st.session_state["kg"], st.session_state["doc_name"])
            st.download_button(
                "Download intelligence report",
                data=report_data,
                file_name="intelligence_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            if st.button("Reset session", use_container_width=True, type="secondary"):
                for k in ["is_indexed", "kg", "messages", "doc_name", "chunks_count"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # ===== Hero =====
    st.markdown('<div class="hero-title">KG · RAG Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Hybrid retrieval — vector search joined with knowledge-graph traversal, answered by Gemini.</div>',
        unsafe_allow_html=True,
    )

    # ===== Status pills =====
    is_idx = st.session_state["is_indexed"]
    kg = st.session_state["kg"]
    nodes, edges = kg.number_of_nodes(), kg.number_of_edges()
    pills = []
    if is_idx:
        pills.append(f'<span class="pill green dot">Indexed · {st.session_state["doc_name"] or "document"}</span>')
        pills.append(f'<span class="pill">{st.session_state["chunks_count"]} chunks</span>')
        pills.append(f'<span class="pill">{nodes} entities · {edges} relations</span>')
    else:
        pills.append('<span class="pill amber dot">Idle · awaiting source</span>')
    pills.append(f'<span class="pill">Model · {LLM_MODEL}</span>')
    st.markdown(
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1.5rem;">'
        + "".join(pills)
        + "</div>",
        unsafe_allow_html=True,
    )

    if not is_idx:
        render_empty_state()
        return

    # ===== Tabs =====
    tab_chat, tab_graph = st.tabs(["Chat", "Knowledge graph"])

    with tab_chat:
        # History
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
                st.markdown(msg["content"])
                if msg["role"] == "assistant":
                    render_sources(msg.get("sources") or [])

        # Input
        prompt = st.chat_input("Ask a question about the indexed documents…")
        if prompt:
            if not validate_input_query(prompt):
                st.warning("Query must be between 3 and 1000 characters.")
            else:
                st.session_state["messages"].append({"role": "user", "content": prompt})
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(prompt)
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Retrieving from graph and vector store…"):
                        try:
                            vector_store = load_vector_store()
                            if vector_store is None:
                                raise RuntimeError("Vector store missing on disk — rebuild the index.")
                            ans, docs = answer_query(prompt, vector_store, st.session_state["kg"])
                        except Exception as e:
                            st.error(f"Generation failed: {e}")
                            return
                    st.markdown(ans)
                    render_sources(docs)
                    if enable_voice:
                        autoplay_audio(ans)
                st.session_state["messages"].append({"role": "assistant", "content": ans, "sources": docs})

    with tab_graph:
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Entities", nodes)
        col_b.metric("Relationships", edges)
        density = (edges / max(nodes * (nodes - 1), 1)) if nodes > 1 else 0
        col_c.metric("Graph density", f"{density:.3f}")
        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        render_kg(kg, height=560)


if __name__ == "__main__":
    main()

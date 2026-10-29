"""Generate the final internship presentation for the KG + RAG project.

Mirrors the slide structure of the PySpiders Review-2 deck (provided as
reference) but with content adapted to this project: a hybrid Knowledge
Graph + Retrieval-Augmented Generation Q&A system built on Streamlit,
LangChain, FAISS, NetworkX, and Google Gemini.

Output: Internship_Final_Review_KG_RAG.pptx at the project root.
"""

from __future__ import annotations

import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parent
SKILL_DIR = ROOT / ".claude" / "skills" / "run-kg-rag-project"
SCREENSHOT = SKILL_DIR / "screenshot.png"
OUT_PATH = ROOT / "Internship_Final_Review_KG_RAG.pptx"

# Institute palette (sampled from the reference PDF)
COL_BG = RGBColor(0xF4, 0xEF, 0xE6)        # cream background
COL_TITLE = RGBColor(0x2E, 0x1A, 0x47)     # deep purple titles
COL_INSTITUTE_RED = RGBColor(0xC0, 0x10, 0x10)
COL_LABEL_ORANGE = RGBColor(0xE6, 0x6A, 0x1F)
COL_BODY = RGBColor(0x2A, 0x2A, 0x35)
COL_SUBTLE = RGBColor(0x6E, 0x6E, 0x7E)
COL_ACCENT = RGBColor(0x8B, 0x5C, 0xF6)    # KG-RAG project violet
COL_LIGHT_DIVIDER = RGBColor(0xD7, 0xCB, 0xB5)

DEPT_FOOTER = "Dept of AIML, CBIT-Kolar"
YEAR = "2026"


def _set_bg(slide, color: RGBColor) -> None:
    """Solid-fill the slide background."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_text(slide, left, top, width, height, text, *,
              size=18, bold=False, color=COL_BODY, align=PP_ALIGN.LEFT,
              anchor=MSO_ANCHOR.TOP, font_name="Calibri"):
    """Add a single-paragraph textbox."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def _add_bullets(slide, left, top, width, height, bullets, *,
                 size=18, color=COL_BODY, bullet_color=COL_ACCENT,
                 line_spacing=1.25, indent_levels=None):
    """Add a multi-bullet textbox. bullets is a list of strings OR
    tuples (level:int, text:str) for nested bullets."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)

    for i, item in enumerate(bullets):
        if isinstance(item, tuple):
            level, text = item
        else:
            level, text = 0, item

        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.level = level
        p.line_spacing = line_spacing

        # bullet marker as accent dot
        bullet = "▸ " if level == 0 else "• "
        run0 = p.add_run()
        run0.text = bullet
        run0.font.name = "Calibri"
        run0.font.size = Pt(size)
        run0.font.bold = True
        run0.font.color.rgb = bullet_color

        run = p.add_run()
        run.text = text
        run.font.name = "Calibri"
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return tb


def _add_footer(slide, idx: int, total: int, label: str = "Internship Final Review"):
    """Page number + department footer at the bottom."""
    _add_text(slide, Inches(0.4), Inches(0.2), Inches(4), Inches(0.3),
              label, size=10, bold=True, color=COL_SUBTLE)
    _add_text(slide, Inches(0.4), Inches(7.05), Inches(5), Inches(0.3),
              DEPT_FOOTER, size=10, color=COL_SUBTLE)
    _add_text(slide, Inches(5.5), Inches(7.05), Inches(2.5), Inches(0.3),
              YEAR, size=10, color=COL_SUBTLE, align=PP_ALIGN.CENTER)
    _add_text(slide, Inches(11.5), Inches(7.05), Inches(1.5), Inches(0.3),
              f"{idx}", size=10, bold=True, color=COL_SUBTLE, align=PP_ALIGN.RIGHT)
    # Thin divider above footer
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.4), Inches(6.95),
                                  Inches(12.6), Emu(9000))
    line.fill.solid()
    line.fill.fore_color.rgb = COL_LIGHT_DIVIDER
    line.line.fill.background()


def _add_title(slide, text: str):
    _add_text(slide, Inches(0.5), Inches(0.55), Inches(12.3), Inches(0.85),
              text, size=34, bold=True, color=COL_TITLE)
    # underline accent
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(0.5), Inches(1.32),
                                    Inches(1.4), Emu(36000))
    accent.fill.solid()
    accent.fill.fore_color.rgb = COL_ACCENT
    accent.line.fill.background()


def _new_content_slide(prs, idx, total, title):
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, COL_BG)
    _add_title(slide, title)
    _add_footer(slide, idx, total)
    return slide


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_title(prs):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _set_bg(slide, COL_BG)

    # University banner
    _add_text(slide, Inches(0.5), Inches(0.4), Inches(12.3), Inches(0.5),
              "VISVESVARAYA TECHNOLOGICAL UNIVERSITY",
              size=22, bold=True, color=COL_INSTITUTE_RED, align=PP_ALIGN.CENTER)
    _add_text(slide, Inches(0.5), Inches(0.95), Inches(12.3), Inches(0.35),
              "Belagavi – 590 018",
              size=14, bold=True, color=COL_INSTITUTE_RED, align=PP_ALIGN.CENTER)

    # Institute
    _add_text(slide, Inches(0.5), Inches(1.4), Inches(12.3), Inches(0.5),
              "C. BYREGOWDA INSTITUTE OF TECHNOLOGY",
              size=20, bold=True, color=COL_TITLE, align=PP_ALIGN.CENTER)
    _add_text(slide, Inches(0.5), Inches(1.95), Inches(12.3), Inches(0.7),
              "Approved by AICTE New Delhi · Accredited by NAAC with B++ Grade · Recognized by Govt. of Karnataka\n"
              "Affiliated to VTU Belagavi · ISO 9001:2015 Certified Institute",
              size=11, color=COL_SUBTLE, align=PP_ALIGN.CENTER)

    # Department
    _add_text(slide, Inches(0.5), Inches(2.7), Inches(12.3), Inches(0.5),
              "DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING",
              size=15, bold=True, color=COL_TITLE, align=PP_ALIGN.CENTER)

    # Review label
    _add_text(slide, Inches(0.5), Inches(3.3), Inches(12.3), Inches(0.45),
              "Internship Final Review",
              size=17, bold=True, color=COL_BODY, align=PP_ALIGN.CENTER)

    # Project metadata (labeled lines)
    meta_top = Inches(3.85)
    for i, (label, value, lcol) in enumerate([
        ("Company: ", "PySpiders, BTM Bengaluru", COL_LABEL_ORANGE),
        ("Domain: ", "Generative AI · Knowledge Graphs · Retrieval-Augmented Generation", COL_LABEL_ORANGE),
        ("Project Title: ", "KG + RAG INTELLIGENCE – HYBRID KNOWLEDGE-GRAPH AND RAG Q&A SYSTEM", COL_LABEL_ORANGE),
    ]):
        tb = slide.shapes.add_textbox(Inches(0.6), meta_top + Inches(i * 0.45),
                                      Inches(12.1), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r1 = p.add_run()
        r1.text = label
        r1.font.name = "Calibri"; r1.font.size = Pt(16); r1.font.bold = True
        r1.font.color.rgb = lcol
        r2 = p.add_run()
        r2.text = value
        r2.font.name = "Calibri"; r2.font.size = Pt(16); r2.font.bold = True
        r2.font.color.rgb = COL_TITLE

    # Bottom: presenter + guide
    _add_text(slide, Inches(0.7), Inches(5.6), Inches(6), Inches(0.35),
              "Presented by:", size=13, bold=True, color=COL_BODY)
    _add_bullets(slide, Inches(0.7), Inches(5.95), Inches(6), Inches(1.5), [
        "Prajwal H D",
        "1CK22AI038",
        "8th Semester",
        "Dept. of AI & ML",
    ], size=13, color=COL_BODY, bullet_color=COL_LIGHT_DIVIDER)

    _add_text(slide, Inches(7.4), Inches(5.6), Inches(5.5), Inches(0.35),
              "Internship Guide:", size=13, bold=True, color=COL_BODY)
    _add_bullets(slide, Inches(7.4), Inches(5.95), Inches(5.5), Inches(1.5), [
        "Prof. Vanitha L B",
        "Assistant Professor",
        "Dept. of AI & ML",
        "CBIT, Kolar",
    ], size=13, color=COL_BODY, bullet_color=COL_LIGHT_DIVIDER)


def slide_organization(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Organization Overview")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12.0), Inches(5),
                 [
                     "PySpiders is a well-known training and development organization specializing in software technologies including Python, Data Science, Artificial Intelligence, and Web Development.",
                     "The organization focuses on bridging the gap between academic learning and industry requirements by providing hands-on training and real-time project exposure.",
                     "During the internship I worked in the Python with Data Science / AI domain, where I gained practical knowledge in building intelligent retrieval and reasoning systems using LangChain, FAISS, and Google Gemini.",
                 ], size=17, line_spacing=1.4)


def slide_abstract(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Abstract")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12.0), Inches(5), [
        "This project presents a Hybrid KG + RAG Intelligence System capable of answering natural-language questions over any uploaded PDF or text document.",
        "The system fuses two complementary indexes built from the same source: a FAISS vector store of semantic chunks and a NetworkX knowledge graph of LLM-extracted subject-predicate-object triplets.",
        "Each query is grounded by retrieving both relevant text chunks and connected graph facts, then forwarded to Google Gemini for citation-backed answer generation.",
        "The goal is to reduce LLM hallucination and improve multi-hop reasoning by combining semantic similarity with explicit relational structure — accessible through a polished Streamlit interface.",
    ], size=16, line_spacing=1.35)


def slide_intro(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Introduction")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12.0), Inches(5), [
        "Knowledge work today depends on synthesizing information across long documents — a task that scales poorly for humans.",
        "Pure Retrieval-Augmented Generation (RAG) systems can fetch relevant passages but struggle with structural questions like 'who reports to whom' or 'what causes X to Y'.",
        "Knowledge Graphs encode such relationships explicitly but are expensive to construct manually and brittle to maintain.",
        "Recent advances in LLM-based information extraction make automatic graph construction feasible, opening the door to hybrid systems that combine the recall of RAG with the precision of graph traversal.",
        "This project introduces such a system — an end-to-end agent that ingests a document, builds both indexes automatically, and answers questions grounded in fused context.",
    ], size=15, line_spacing=1.3)


def slide_objective(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Internship Objective")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12.0), Inches(2), [
        "Design and develop a Hybrid KG + RAG Q&A System that combines vector retrieval with knowledge-graph traversal — without requiring any manual annotation.",
        "Solve a real-world problem: extracting accurate, citation-backed insights from long documents for non-technical users.",
    ], size=15, line_spacing=1.3)

    _add_text(slide, Inches(0.6), Inches(4.1), Inches(12), Inches(0.4),
              "Specific goals — automate:", size=15, bold=True, color=COL_TITLE)
    _add_bullets(slide, Inches(0.9), Inches(4.55), Inches(12), Inches(2.3), [
        "Document ingestion and chunking (PDF + TXT, recursive character splitting)",
        "Vector embedding and FAISS indexing for semantic retrieval",
        "LLM-driven triplet extraction (subject-predicate-object) to populate a NetworkX directed graph",
        "Hybrid context fusion and grounded answer generation via Google Gemini",
        "Citation-rich UI with chat history, interactive graph view, and report export",
    ], size=14, line_spacing=1.25)


def slide_techstack(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Technology Stack")
    _add_text(slide, Inches(0.6), Inches(1.7), Inches(12), Inches(0.45),
              "The project was developed using a modern Python AI/ML stack:",
              size=15, color=COL_BODY)
    _add_bullets(slide, Inches(0.6), Inches(2.2), Inches(12), Inches(4.7), [
        ("Language: Python 3.12"),
        ("UI Framework: Streamlit 1.31 (chat, tabs, st.status, custom CSS)"),
        ("Orchestration: LangChain 0.1.11 (loaders, splitters, prompt templates)"),
        ("Vector Database: FAISS-CPU 1.8.0 (local persistence, no Docker required)"),
        ("Knowledge Graph: NetworkX 3.2.1 — directed graph of extracted triplets"),
        ("LLM + Embeddings: Google Gemini via langchain-google-genai"),
        ("Graph Visualization: PyVis 0.3.1 (vis-network, in-line bundling)"),
        ("Document Parsing: PyPDF 4.1.0 for PDF, native TextLoader for .txt"),
        ("Auxiliary: gTTS for voice readback · Playwright for UI smoke tests · Pytest for validation"),
    ], size=14, line_spacing=1.3)


def slide_description(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Project Description")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12), Inches(0.9), [
        "The project builds an intelligent retrieval agent that ingests any PDF/TXT document and answers questions about it with grounded, citation-backed responses.",
    ], size=15, line_spacing=1.35)

    _add_text(slide, Inches(0.6), Inches(3.15), Inches(12), Inches(0.4),
              "The system acts like a virtual research assistant by performing:",
              size=15, bold=True, color=COL_TITLE)
    _add_bullets(slide, Inches(0.9), Inches(3.6), Inches(12), Inches(2.7), [
        "Document parsing and recursive chunking that preserves semantic boundaries",
        "Parallel index construction: FAISS embeddings + LLM-extracted knowledge graph",
        "Hybrid retrieval that fuses chunk-similarity hits with relational graph facts",
        "Grounded answer generation through Google Gemini with source-document citations",
        "Interactive knowledge-graph visualization with force-directed physics layout",
        "Markdown report export of the extracted intelligence",
    ], size=14, line_spacing=1.25)

    _add_bullets(slide, Inches(0.6), Inches(6.25), Inches(12), Inches(0.5), [
        "This reduces hallucination, supports multi-hop reasoning, and speeds up decision-making for non-technical users.",
    ], size=14, line_spacing=1.3, bullet_color=COL_TITLE)


def slide_methodology(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Methodology / Approach")
    _add_text(slide, Inches(0.6), Inches(1.7), Inches(12), Inches(0.45),
              "The system follows a structured pipeline:",
              size=15, color=COL_BODY)
    _add_bullets(slide, Inches(0.6), Inches(2.15), Inches(12), Inches(4.7), [
        "User uploads a PDF / TXT document through the Streamlit sidebar",
        "PyPDFLoader / TextLoader reads the raw content into LangChain Documents",
        "RecursiveCharacterTextSplitter chunks the text (chunk_size = 1000, overlap = 200)",
        "Chunks fan out in parallel: FAISS Embedder builds the vector store, LLM extracts JSON triplets that populate a NetworkX DiGraph",
        "On query: the Validator gates length/format, FAISS returns top-K semantic matches, the KG retriever pulls neighboring relations for matched entities",
        "Vector context + graph facts are fused into a single prompt and sent to Gemini for answer generation",
        "Streamlit renders the answer, source-chunk citations, and the live knowledge-graph visualization",
    ], size=14, line_spacing=1.25)

    _add_text(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.4),
              "An agile, iterative development approach with hot-reload was used to refine the UI and prompts.",
              size=13, bold=True, color=COL_ACCENT)


def slide_architecture(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "System Architecture")

    # Draw a minimal flow diagram with shapes
    def box(x, y, w, h, text, fill=RGBColor(0xFF, 0xFF, 0xFF), border=COL_ACCENT, font=12):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                       Inches(x), Inches(y), Inches(w), Inches(h))
        shape.fill.solid(); shape.fill.fore_color.rgb = fill
        shape.line.color.rgb = border
        shape.line.width = Pt(1.25)
        tf = shape.text_frame
        tf.margin_left = Emu(0); tf.margin_right = Emu(0)
        tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = text
        r.font.name = "Calibri"; r.font.size = Pt(font); r.font.bold = True
        r.font.color.rgb = COL_TITLE
        return shape

    def arrow(x1, y1, x2, y2):
        conn = slide.shapes.add_connector(2,  # MSO_CONNECTOR.STRAIGHT
                                          Inches(x1), Inches(y1),
                                          Inches(x2), Inches(y2))
        conn.line.color.rgb = COL_SUBTLE
        conn.line.width = Pt(1.25)

    y0 = 1.85
    box(5.3, y0, 2.7, 0.55, "1. Document Upload (PDF / TXT)")
    arrow(6.65, y0 + 0.55, 6.65, y0 + 0.8)
    box(5.3, y0 + 0.8, 2.7, 0.55, "2. Loader → Chunker")
    arrow(6.65, y0 + 1.35, 6.65, y0 + 1.6)

    # Split into two branches
    box(2.4, y0 + 1.6, 3.5, 0.6, "3a. FAISS Vector Index",
        fill=RGBColor(0xEE, 0xE7, 0xFB))
    box(7.5, y0 + 1.6, 3.5, 0.6, "3b. KG Triplet Extraction → NetworkX",
        fill=RGBColor(0xFF, 0xEA, 0xE3))
    arrow(6.65, y0 + 1.35, 4.15, y0 + 1.6)
    arrow(6.65, y0 + 1.35, 9.25, y0 + 1.6)

    # Query path
    box(5.3, y0 + 2.5, 2.7, 0.55, "4. User Query")
    arrow(5.3 + 1.35, y0 + 3.05, 5.3 + 1.35, y0 + 3.3)

    # Retrievers parallel
    box(2.4, y0 + 3.3, 3.5, 0.55, "5a. Vector Retriever (top-K)",
        fill=RGBColor(0xEE, 0xE7, 0xFB))
    box(7.5, y0 + 3.3, 3.5, 0.55, "5b. KG Retriever (keyword → neighbors)",
        fill=RGBColor(0xFF, 0xEA, 0xE3))
    arrow(5.3 + 1.35, y0 + 3.3, 4.15, y0 + 3.3)
    arrow(5.3 + 1.35, y0 + 3.3, 9.25, y0 + 3.3)

    box(5.0, y0 + 4.05, 3.3, 0.55, "6. Context Fusion → Gemini LLM",
        fill=RGBColor(0xDC, 0xD0, 0xF8))
    arrow(4.15, y0 + 3.85, 6.65, y0 + 4.05)
    arrow(9.25, y0 + 3.85, 6.65, y0 + 4.05)

    box(5.0, y0 + 4.85, 3.3, 0.55, "7. Streamlit UI (answer + citations + graph)")
    arrow(6.65, y0 + 4.6, 6.65, y0 + 4.85)


def slide_work_done(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Work Done")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12), Inches(1.0), [
        "During the internship I independently designed and implemented the complete system end-to-end. My key contributions:",
    ], size=15, line_spacing=1.35)
    _add_bullets(slide, Inches(0.9), Inches(2.8), Inches(12), Inches(4.0), [
        "Document loading pipeline supporting PDF (PyPDF) and TXT inputs with extension validation",
        "Recursive chunking pipeline tuned for LLM token windows (chunk_size=1000, overlap=200)",
        "FAISS vector store with persistence and re-load logic to avoid duplicate embedding cost",
        "LLM-driven triplet extraction with prompt-engineered JSON output, parsed into a NetworkX DiGraph",
        "Hybrid retriever fusing top-K FAISS results with keyword-matched graph facts",
        "Premium Streamlit UI: chat input, source citations, force-directed PyVis graph, status pills, hero gradient",
        "Programmatic driver (driver.py) with health probe, screenshot, and smoke commands via Playwright",
        "Pytest validation suite (5 tests, 100% passing) covering imports, config, chunker, validator, KG structure",
    ], size=13, line_spacing=1.2)


def slide_results(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Results")
    _add_text(slide, Inches(0.6), Inches(1.7), Inches(12), Inches(0.45),
              "The system successfully delivers the following outputs:",
              size=15, color=COL_BODY)
    _add_bullets(slide, Inches(0.6), Inches(2.2), Inches(12), Inches(4.5), [
        "End-to-end Q&A over uploaded documents with grounded, citation-backed answers",
        "Automatic knowledge graph extraction (typical: 60+ entities and 40+ relations on a 4-chunk document)",
        "Interactive force-directed graph visualization with hover tooltips, degree-based sizing, and 6-color palette",
        "Source-chunk citations rendered inline with chunk number, source file, page number, and 420-char snippet",
        "Markdown intelligence-report export listing extracted triplets",
        "Optional voice readback of answers via gTTS",
        "All five pytest validation tests pass under Python 3.12 in ~47 seconds",
    ], size=14, line_spacing=1.3)
    _add_text(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.4),
              "Results demonstrate that the system can handle real-world documents and reduce hallucination through fused retrieval.",
              size=13, bold=True, color=COL_ACCENT)


def slide_snapshots(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Snapshots")
    if SCREENSHOT.exists():
        # Centered, scaled to 8 inches wide
        pic = slide.shapes.add_picture(str(SCREENSHOT),
                                       Inches(2.5), Inches(1.85),
                                       width=Inches(8.0))
        # Caption beneath the image
        _add_text(slide, Inches(2.5), Inches(1.85) + pic.height + Inches(0.1),
                  Inches(8.0), Inches(0.4),
                  "Figure 1: KG + RAG Intelligence — empty state with status pills, sidebar controls, and onboarding card",
                  size=12, color=COL_SUBTLE, align=PP_ALIGN.CENTER)
    else:
        _add_text(slide, Inches(0.6), Inches(3.5), Inches(12), Inches(1),
                  "(screenshot.png not found at " + str(SCREENSHOT) + ")",
                  size=14, color=COL_SUBTLE, align=PP_ALIGN.CENTER)


def slide_snapshots_2(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Snapshots (continued)")
    # Description of additional UI panels
    _add_text(slide, Inches(0.6), Inches(1.85), Inches(12), Inches(0.45),
              "Additional UI panels captured during user testing:",
              size=15, color=COL_BODY)
    _add_bullets(slide, Inches(0.6), Inches(2.4), Inches(12), Inches(4.3), [
        "Indexing status block — live stepped progress: Loading → Chunking → Embedding → Extracting KG",
        "Chat tab — assistant messages with bot avatar, expandable Sources panel showing chunk metadata",
        "Knowledge graph tab — Entities / Relationships / Graph density metric tiles and interactive PyVis canvas",
        "Sidebar — Voice readback toggle, Document source uploader, Export controls, Reset session",
        "Intelligence Report — Markdown export with entity counts and up to 50 triplets",
    ], size=14, line_spacing=1.3)
    _add_text(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.4),
              "Refer to the live demo at http://localhost:8501 for full interactivity.",
              size=12, bold=True, color=COL_ACCENT)


def slide_challenges(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Challenges Faced")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12), Inches(5), [
        "Handling PDFs whose pages contain images instead of extractable text (PyPDFLoader returns empty chunks).",
        "Streamlit's WebSocket-driven hydration broke naive `chrome --headless --screenshot` testing — virtual time does not advance the websocket exchange.",
        "PyVis save_graph attempted to write into ./lib/bindings, which failed with WinError 5 on a OneDrive-synced project root where lib/ was already locked.",
        "Streamlit's chat_message rejected the custom Unicode glyph `◈` because it is not in the emoji whitelist, falling through to a missing-file open.",
        "The shipped venv was a Python 3.9 shim hard-coded to another user's machine path, blocking every Python invocation until rebuilt.",
        "Limited prompt-engineering budget to coax stable JSON triplets out of the LLM across diverse document genres.",
    ], size=13, line_spacing=1.25)


def slide_solutions(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Solutions & Learning")
    _add_text(slide, Inches(0.6), Inches(1.7), Inches(12), Inches(0.45),
              "Solutions applied:",
              size=15, bold=True, color=COL_TITLE)
    _add_bullets(slide, Inches(0.6), Inches(2.15), Inches(12), Inches(2.7), [
        "Documented the PDF-extraction caveat in the run skill and validated extensions early via validate_file_extension.",
        "Replaced ad-hoc screenshotting with a Playwright-based driver that waits for the .hero-title selector before capturing.",
        "Switched PyVis to cdn_resources='in_line' and generate_html() — no filesystem writes, no lib/ permission issues.",
        "Swapped invalid Unicode avatars for real emoji (🤖, 🧑, 🧠) accepted by Streamlit's validator.",
        "Rebuilt the venv with the local Python 3.12 interpreter and force-reinstalled all wheels.",
    ], size=13, line_spacing=1.2)
    _add_text(slide, Inches(0.6), Inches(5.1), Inches(12), Inches(0.45),
              "Key learnings:",
              size=15, bold=True, color=COL_TITLE)
    _add_bullets(slide, Inches(0.6), Inches(5.55), Inches(12), Inches(1.5), [
        "Hybrid AI architectures combining vector retrieval with structured graphs",
        "LLM-driven information extraction and prompt design for structured JSON output",
        "Streamlit advanced UI patterns: chat, status blocks, custom CSS, components.html",
        "Headless web-app testing with Playwright and CDP-driven hydration waits",
    ], size=13, line_spacing=1.2)


def slide_applications(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Applications")
    _add_bullets(slide, Inches(0.6), Inches(1.8), Inches(12), Inches(1.0), [
        "The system has broad applicability wherever long-form documents need to be questioned and cross-referenced:",
    ], size=15, line_spacing=1.35)
    _add_bullets(slide, Inches(0.9), Inches(2.8), Inches(12), Inches(4), [
        "Enterprise document Q&A — internal policies, SOPs, technical manuals",
        "Legal and contract analysis — clause lookup, cross-reference, obligation extraction",
        "Academic research — literature review and citation discovery across PDFs",
        "Medical record summarization — patient history Q&A with relational grounding",
        "Compliance and audit — regulation traceability across multi-section documents",
        "Construction project management — RFI / drawing-set / specification queries (directly relevant to A N Prakash CPMC)",
    ], size=14, line_spacing=1.3)
    _add_text(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.4),
              "It empowers non-technical users to extract structured insights without writing code.",
              size=13, bold=True, color=COL_ACCENT)


def slide_conclusion(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Conclusion")
    _add_bullets(slide, Inches(0.6), Inches(1.9), Inches(12), Inches(5), [
        "The project successfully demonstrates that combining vector retrieval with automatically-extracted knowledge graphs produces a more grounded and reasoning-friendly Q&A agent than either approach alone.",
        "The Hybrid KG + RAG Intelligence system reduces hallucination, supports multi-hop reasoning via graph traversal, and presents results in a polished, citation-rich Streamlit interface.",
        "End-to-end automation — from document ingestion to graph visualization — makes the system usable by non-technical stakeholders without sacrificing rigor.",
        "The project deepened my understanding of LLM orchestration, retrieval architectures, and production-quality web UI engineering, and serves as a strong foundation for further work on agentic retrieval systems.",
    ], size=15, line_spacing=1.4)


def slide_thank_you(prs, idx, total):
    slide = _new_content_slide(prs, idx, total, "Thank You")
    # Big Q&A center mark
    big = slide.shapes.add_textbox(Inches(0.5), Inches(2.0), Inches(12.3), Inches(2.5))
    tf = big.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Q & A"
    r.font.name = "Calibri"
    r.font.size = Pt(120)
    r.font.bold = True
    r.font.color.rgb = COL_ACCENT

    _add_text(slide, Inches(0.5), Inches(4.8), Inches(12.3), Inches(0.6),
              "Questions, suggestions, and discussion welcomed.",
              size=18, color=COL_BODY, align=PP_ALIGN.CENTER)
    _add_text(slide, Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.5),
              "— Prajwal H D · 1CK22AI038 · 8th Semester · Dept. of AI & ML, CBIT Kolar —",
              size=13, color=COL_SUBTLE, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    builders = [
        slide_title,        # idx 1
        slide_organization, # 2
        slide_abstract,     # 3
        slide_intro,        # 4
        slide_objective,    # 5
        slide_techstack,    # 6
        slide_description,  # 7
        slide_methodology,  # 8
        slide_architecture, # 9
        slide_work_done,    # 10
        slide_results,      # 11
        slide_snapshots,    # 12
        slide_snapshots_2,  # 13
        slide_challenges,   # 14
        slide_solutions,    # 15
        slide_applications, # 16
        slide_conclusion,   # 17
        slide_thank_you,    # 18
    ]
    total = len(builders)

    for i, build in enumerate(builders, start=1):
        if i == 1:
            build(prs)
        else:
            build(prs, i, total)

    prs.save(OUT_PATH)
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"wrote {OUT_PATH} ({size_kb:.1f} KB, {total} slides)")


if __name__ == "__main__":
    main()

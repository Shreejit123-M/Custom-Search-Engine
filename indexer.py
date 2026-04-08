"""
indexer.py
Handles file parsing (PDF, DOCX, TXT) and chunking before indexing.
Chunking is essential for RAG — large docs are split into overlapping windows.
"""

import os
import uuid

CHUNK_SIZE    = 400   # tokens per chunk
CHUNK_OVERLAP = 80    # overlap between consecutive chunks


# ── File parsers ──────────────────────────────────────────────────────────────

def extract_text_from_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        try:
            import PyPDF2
            text_parts = []
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            return "\n".join(text_parts)
        except ImportError:
            return ""


def extract_text_from_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return ""


def extract_text(filepath: str) -> tuple[str, str]:
    """Returns (text, filetype)."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath), "pdf"
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath), "docx"
    else:
        return extract_text_from_txt(filepath), "txt"


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping token-based chunks."""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


# ── Main indexing entry point ─────────────────────────────────────────────────

def index_document(filepath: str, inverted_index, text_processor, search_engine) -> dict:
    """
    Parse, chunk, index, and embed a document.
    Returns metadata dict with doc_id list and stats.
    """
    filename = os.path.basename(filepath)
    raw_text, filetype = extract_text(filepath)

    if not raw_text.strip():
        return {"error": "Could not extract text from file."}

    chunks = chunk_text(raw_text)
    base_title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

    doc_ids = []
    for i, chunk in enumerate(chunks):
        doc_id = str(uuid.uuid4())
        tokens = text_processor.process(chunk)

        metadata = {
            "title":        f"{base_title} (chunk {i+1}/{len(chunks)})" if len(chunks) > 1 else base_title,
            "filename":     filename,
            "filetype":     filetype,
            "chunk_index":  i,
            "text_preview": chunk[:250] + "…" if len(chunk) > 250 else chunk,
            "full_text":    chunk,
        }
        inverted_index.add_document(doc_id, tokens, metadata)

        # Embed chunk for semantic search
        search_engine.add_embedding(doc_id, chunk)
        doc_ids.append(doc_id)

    return {
        "doc_ids":    doc_ids,
        "filename":   filename,
        "filetype":   filetype,
        "chunks":     len(chunks),
        "char_count": len(raw_text),
    }


def remove_document_by_filename(filename: str, inverted_index, search_engine) -> int:
    """Remove all chunks belonging to a given filename. Returns number removed."""
    ids_to_remove = [
        doc_id for doc_id, stats in inverted_index.document_stats.items()
        if stats.get("filename") == filename
    ]
    for doc_id in ids_to_remove:
        inverted_index.remove_document(doc_id)
        search_engine.remove_embedding(doc_id)
    return len(ids_to_remove)


def list_indexed_files(inverted_index) -> list[dict]:
    """Return one entry per unique filename (aggregating chunks)."""
    seen: dict[str, dict] = {}
    for doc_id, stats in inverted_index.document_stats.items():
        fn = stats.get("filename", "unknown")
        if fn not in seen:
            seen[fn] = {
                "filename": fn,
                "filetype": stats.get("filetype", "txt"),
                "chunks":   0,
                "title":    stats.get("title", fn).split(" (chunk")[0],
            }
        seen[fn]["chunks"] += 1
    return list(seen.values())

# RAGSearch — Hybrid Document Search & AI Q&A Engine

A production-grade search engine that combines **BM25 keyword retrieval**, **semantic vector search**, and a **Retrieval-Augmented Generation (RAG)** pipeline for AI-powered document Q&A.

Built from scratch in Python. No external search services. Runs entirely on your machine.

---

## Architecture

```
Upload Document
      │
      ▼
Text Extraction (PDF / DOCX / TXT)
      │
      ▼
Chunking (400-token windows, 80-token overlap)
      │
      ├── Tokenize + BM25 Index (InvertedIndex)
      │
      └── Encode → Sentence Embedding (all-MiniLM-L6-v2)
                          │
                          ▼
                   ChromaDB / numpy store

Query
  │
  ├── BM25 score (TF-IDF + length normalisation)
  │
  ├── Cosine similarity (semantic embedding)
  │
  └── Hybrid score = 0.55 * BM25_norm + 0.45 * semantic_sim
                          │
                          ▼
                     Top-K chunks
                          │
                          ▼
                  LLM (Claude / GPT-4o)
                          │
                          ▼
                  Grounded answer + citations
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask |
| Keyword Search | BM25 (Okapi, k1=1.5, b=0.75) over inverted index |
| Semantic Search | `sentence-transformers` (all-MiniLM-L6-v2, 384-dim) |
| Hybrid Ranking | Weighted linear combination |
| RAG / LLM | Anthropic Claude (or OpenAI GPT-4o) |
| File Parsing | pdfplumber, python-docx |
| Storage | JSON-serialised index + embeddings (zero DB dependency) |
| Frontend | Vanilla JS, CSS variables, dark terminal aesthetic |

## Quickstart

```bash
# 1. Clone
git clone https://github.com/Shreejit123-M/rag-search-engine.git
cd rag-search-engine

# 2. Install
pip install -r requirements.txt

# 3. (Optional) Set LLM key for AI Q&A
export ANTHROPIC_API_KEY=sk-ant-...

# 4. Run
python app.py
# → http://localhost:5000
```

## Features

- **Hybrid search** — BM25 + sentence-transformer cosine similarity, linearly combined
- **RAG Q&A** — retrieve top-5 relevant chunks → feed to Claude/GPT → grounded answer with citations
- **Smart chunking** — 400-token overlapping windows preserve context across chunk boundaries
- **Multi-format** — PDF, DOCX, TXT ingestion with automatic text extraction
- **Zero external DB** — inverted index and embeddings serialised to JSON; no Postgres, Elasticsearch, or Redis required
- **Graceful degradation** — falls back to BM25-only if sentence-transformers not installed; falls back to chunk preview if no LLM key set

## Performance

| Metric | Value |
|---|---|
| Avg search latency | < 80ms (BM25), < 200ms (hybrid) |
| Embedding model size | ~80 MB |
| Index overhead | ~5 MB per 1000 document chunks |
| RAG answer latency | 1–3 s (LLM dependent) |

## Project Structure

```
├── app.py              # Flask routes
├── search_engine.py    # BM25 + hybrid ranking
├── inverted_index.py   # Index build / query / persist
├── text_processor.py   # Tokeniser, stopwords, cleaning
├── indexer.py          # File parsing + chunking
├── rag.py              # RAG pipeline (retrieval → LLM → answer)
├── requirements.txt
└── templates/
    └── index.html      # Single-page UI
```

## Author

**Shreejit Magadum** — [LinkedIn](https://linkedin.com/in/shreejitm) · [GitHub](https://github.com/Shreejit123-M)

IEEE Published Researcher · ECE @ REVA University · Embedded + ML Engineer

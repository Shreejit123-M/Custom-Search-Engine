"""
search_engine.py
Hybrid search: BM25 keyword retrieval + cosine semantic re-ranking.
Uses sentence-transformers for embeddings (falls back gracefully if not installed).
"""

import heapq
import math
import json
import os
import numpy as np
from collections import defaultdict

# ── Semantic embeddings (optional but strongly recommended) ──────────────────
try:
    from sentence_transformers import SentenceTransformer
    _SBERT_AVAILABLE = True
except ImportError:
    _SBERT_AVAILABLE = False

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"   # fast, free, 80MB download


class SearchEngine:
    """
    Hybrid BM25 + Semantic search engine.

    BM25 weights (k1=1.5, b=0.75) are classic Okapi BM25 defaults.
    Semantic similarity uses cosine distance on 384-dim sentence embeddings.
    Final score = alpha * bm25_norm + (1-alpha) * semantic_sim
    """

    BM25_K1 = 1.5
    BM25_B  = 0.75
    HYBRID_ALPHA = 0.55   # weight for BM25 vs semantic

    def __init__(self, inverted_index, text_processor, embed_path: str = "data/embeddings.npy"):
        self.index = inverted_index
        self.processor = text_processor
        self.embed_path = embed_path
        self.embeddings: dict[str, np.ndarray] = {}   # doc_id -> vector
        self.sbert = None

        if _SBERT_AVAILABLE:
            print("[SearchEngine] Loading sentence-transformer model…")
            self.sbert = SentenceTransformer(EMBED_MODEL_NAME)
            self._load_embeddings()
            print("[SearchEngine] Semantic search enabled ✓")
        else:
            print("[SearchEngine] sentence-transformers not installed — BM25 only mode")

    # ── Public API ─────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        query_words = self.processor.process(query)
        if not query_words:
            return []

        candidates = self._get_candidates(query_words)
        bm25_scores = self._score_bm25(query_words, candidates)

        if self.sbert and self.embeddings:
            results = self._hybrid_rank(query, bm25_scores, top_k)
        else:
            results = heapq.nlargest(top_k, bm25_scores, key=lambda x: x["score"])

        # Enrich with doc metadata
        for r in results:
            stats = self.index.document_stats.get(r["doc_id"], {})
            r.update({
                "title":        stats.get("title", r["doc_id"]),
                "filename":     stats.get("filename", ""),
                "text_preview": stats.get("text_preview", ""),
                "filetype":     stats.get("filetype", "txt"),
            })
        return results

    def add_embedding(self, doc_id: str, text: str):
        """Compute and store embedding for a document chunk."""
        if not self.sbert:
            return
        vec = self.sbert.encode(text, normalize_embeddings=True)
        self.embeddings[doc_id] = vec
        self._save_embeddings()

    def remove_embedding(self, doc_id: str):
        if doc_id in self.embeddings:
            del self.embeddings[doc_id]
            self._save_embeddings()

    @property
    def semantic_enabled(self) -> bool:
        return self.sbert is not None

    # ── BM25 internals ─────────────────────────────────────────────────────────

    def _get_candidates(self, query_words: list[str]) -> dict:
        candidates = defaultdict(lambda: {"words": set(), "tf": {}})
        for word in query_words:
            postings = self.index.get_postings(word)
            for doc_id, data in postings["postings"].items():
                candidates[doc_id]["words"].add(word)
                candidates[doc_id]["tf"][word] = data["tf"]
        return dict(candidates)

    def _score_bm25(self, query_words: list[str], candidates: dict) -> list[dict]:
        if self.index.total_docs == 0:
            return []

        total_length = sum(s["length"] for s in self.index.document_stats.values())
        avg_dl = total_length / self.index.total_docs

        results = []
        for doc_id, doc_data in candidates.items():
            score = 0.0
            doc_length = self.index.document_stats.get(doc_id, {}).get("length", 1)

            for word in query_words:
                if word not in doc_data["words"]:
                    continue
                tf = doc_data["tf"][word]
                df = self.index.get_document_frequency(word)
                N  = self.index.total_docs
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
                numerator   = tf * (self.BM25_K1 + 1)
                denominator = tf + self.BM25_K1 * (1 - self.BM25_B + self.BM25_B * doc_length / avg_dl)
                score += idf * (numerator / denominator)

            if score > 0:
                results.append({
                    "doc_id":        doc_id,
                    "score":         round(score, 4),
                    "matched_words": list(doc_data["words"]),
                    "match_count":   len(doc_data["words"]),
                    "search_type":   "bm25",
                })
        return results

    # ── Hybrid re-ranking ──────────────────────────────────────────────────────

    def _hybrid_rank(self, query: str, bm25_results: list[dict], top_k: int) -> list[dict]:
        if not bm25_results and not self.embeddings:
            return []

        query_vec = self.sbert.encode(query, normalize_embeddings=True)

        # Semantic scores for ALL indexed docs
        sem_scores: dict[str, float] = {}
        for doc_id, vec in self.embeddings.items():
            sem_scores[doc_id] = float(np.dot(query_vec, vec))

        # Normalise BM25 scores to [0,1]
        bm25_map = {r["doc_id"]: r for r in bm25_results}
        max_bm25 = max((r["score"] for r in bm25_results), default=1.0) or 1.0

        # Union of BM25 candidates + semantic candidates
        all_ids = set(bm25_map.keys()) | set(sem_scores.keys())
        combined = []
        for doc_id in all_ids:
            bm25_norm = bm25_map[doc_id]["score"] / max_bm25 if doc_id in bm25_map else 0.0
            sem       = sem_scores.get(doc_id, 0.0)
            hybrid    = self.HYBRID_ALPHA * bm25_norm + (1 - self.HYBRID_ALPHA) * sem
            entry = bm25_map.get(doc_id, {"doc_id": doc_id, "matched_words": [], "match_count": 0})
            entry = dict(entry)
            entry["score"]       = round(hybrid, 4)
            entry["bm25_score"]  = round(bm25_norm, 4)
            entry["sem_score"]   = round(sem, 4)
            entry["search_type"] = "hybrid"
            combined.append(entry)

        return heapq.nlargest(top_k, combined, key=lambda x: x["score"])

    # ── Persistence ────────────────────────────────────────────────────────────

    def _save_embeddings(self):
        os.makedirs(os.path.dirname(self.embed_path) or ".", exist_ok=True)
        data = {doc_id: vec.tolist() for doc_id, vec in self.embeddings.items()}
        with open(self.embed_path, "w") as f:
            json.dump(data, f)

    def _load_embeddings(self):
        if not os.path.exists(self.embed_path):
            return
        with open(self.embed_path, "r") as f:
            data = json.load(f)
        self.embeddings = {k: np.array(v, dtype=np.float32) for k, v in data.items()}

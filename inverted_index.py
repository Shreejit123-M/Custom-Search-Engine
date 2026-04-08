"""
inverted_index.py
Builds and manages the inverted index for BM25 retrieval.
"""

import json
import os
from collections import defaultdict


class InvertedIndex:
    def __init__(self):
        self.index: dict[str, dict] = defaultdict(lambda: {"df": 0, "postings": {}})
        self.document_stats: dict[str, dict] = {}   # doc_id -> {length, title, filename, text_preview}
        self.total_docs: int = 0

    def add_document(self, doc_id: str, tokens: list[str], metadata: dict):
        """Index a tokenized document."""
        from collections import Counter
        tf_map = Counter(tokens)
        doc_length = len(tokens)

        for term, tf in tf_map.items():
            if doc_id not in self.index[term]["postings"]:
                self.index[term]["df"] += 1
            self.index[term]["postings"][doc_id] = {"tf": tf}

        self.document_stats[doc_id] = {
            "length": doc_length,
            "title": metadata.get("title", doc_id),
            "filename": metadata.get("filename", ""),
            "text_preview": metadata.get("text_preview", ""),
            "filetype": metadata.get("filetype", "txt"),
            "chunk_index": metadata.get("chunk_index", 0),
            "full_text": metadata.get("full_text", ""),
        }
        self.total_docs += 1

    def get_postings(self, term: str) -> dict:
        return self.index.get(term, {"df": 0, "postings": {}})

    def get_document_frequency(self, term: str) -> int:
        return self.index.get(term, {}).get("df", 0)

    def remove_document(self, doc_id: str):
        """Remove all entries for a given doc_id."""
        terms_to_clean = []
        for term, data in self.index.items():
            if doc_id in data["postings"]:
                del data["postings"][doc_id]
                data["df"] -= 1
                if data["df"] == 0:
                    terms_to_clean.append(term)
        for term in terms_to_clean:
            del self.index[term]
        if doc_id in self.document_stats:
            del self.document_stats[doc_id]
            self.total_docs -= 1

    def save(self, path: str):
        payload = {
            "index": {k: v for k, v in self.index.items()},
            "document_stats": self.document_stats,
            "total_docs": self.total_docs,
        }
        with open(path, "w") as f:
            json.dump(payload, f)

    def load(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            payload = json.load(f)
        self.index = defaultdict(lambda: {"df": 0, "postings": {}})
        self.index.update(payload.get("index", {}))
        self.document_stats = payload.get("document_stats", {})
        self.total_docs = payload.get("total_docs", 0)

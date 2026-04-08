"""
test_search.py
Quick sanity test — runs without Flask. No file needed.
"""

from text_processor  import TextProcessor
from inverted_index  import InvertedIndex
from search_engine   import SearchEngine

def test_bm25():
    tp  = TextProcessor()
    idx = InvertedIndex()

    docs = [
        ("d1", "Machine learning models are trained on large datasets to make predictions."),
        ("d2", "Python is a popular programming language for data science and machine learning."),
        ("d3", "Flask is a lightweight web framework for building REST APIs in Python."),
        ("d4", "BM25 is a ranking function used in information retrieval and search engines."),
        ("d5", "Retrieval-Augmented Generation combines search with large language models."),
    ]
    for doc_id, text in docs:
        tokens = tp.process(text)
        idx.add_document(doc_id, tokens, {"title": doc_id, "filename": "test.txt",
                                           "text_preview": text[:100], "full_text": text})

    eng = SearchEngine(idx, tp, embed_path="data/test_embeddings.json")

    queries = ["machine learning Python", "search ranking BM25", "RAG language model"]
    for q in queries:
        results = eng.search(q, top_k=3)
        print(f"\nQuery: '{q}'")
        for r in results:
            print(f"  [{r['score']}] {r['doc_id']} — {r['search_type']}")

    print("\n✓ All tests passed")

if __name__ == "__main__":
    import os; os.makedirs("data", exist_ok=True)
    test_bm25()

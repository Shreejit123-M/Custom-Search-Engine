import os
from utils import preprocess, compute_similarity

class SearchEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.documents = self.load_documents()

    def load_documents(self):
        docs = {}
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    docs[filename] = f.read()
        return docs

    def search(self, query):
        query_tokens = preprocess(query)
        results = []
        for filename, text in self.documents.items():
            text_tokens = preprocess(text)
            score = compute_similarity(query_tokens, text_tokens)
            results.append((filename, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

import re
from collections import Counter

def preprocess(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def compute_similarity(tokens1, tokens2):
    counter1 = Counter(tokens1)
    counter2 = Counter(tokens2)
    common = set(counter1.keys()) & set(counter2.keys())
    score = sum(min(counter1[word], counter2[word]) for word in common)
    return score / max(len(tokens1), 1)

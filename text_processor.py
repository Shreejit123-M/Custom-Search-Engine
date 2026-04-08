"""
text_processor.py
Handles tokenization, stopword removal, and stemming.
"""

import re
import string
from collections import Counter

# Common English stopwords (no external dependency needed)
STOPWORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","it","its","was","are","were","be","been","being",
    "have","has","had","do","does","did","will","would","could","should",
    "may","might","shall","can","need","dare","ought","used","not","no",
    "nor","so","yet","both","either","neither","each","few","more","most",
    "other","some","such","than","then","too","very","just","as","that",
    "this","these","those","i","you","he","she","we","they","me","him",
    "her","us","them","my","your","his","our","their","what","which","who",
    "whom","how","when","where","why","all","any","if","into","through",
    "during","before","after","above","below","between","out","off","over",
    "under","again","further","there","here","once","only","own","same",
    "about","up","down","also","s","t","re","ll","ve","d","m"
}

class TextProcessor:
    def __init__(self):
        self.stopwords = STOPWORDS

    def process(self, text: str) -> list[str]:
        """Clean, tokenize, and filter text into terms."""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)   # remove URLs
        text = re.sub(r'\d+', ' ', text)                     # remove numbers
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = text.split()
        tokens = [t.strip() for t in tokens if len(t) > 2 and t not in self.stopwords]
        return tokens

    def get_term_frequencies(self, tokens: list[str]) -> dict:
        """Return raw term frequency dict."""
        return dict(Counter(tokens))

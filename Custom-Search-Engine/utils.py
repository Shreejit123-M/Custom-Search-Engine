# utils.py
import re


def clean_query(query):
    return re.sub(r'[^a-zA-Z0-9 ]', '', query.lower())

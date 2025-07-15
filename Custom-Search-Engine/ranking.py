# ranking.py
def rank_results(query, results):
    keyword_score = len(query.split())
    for i, result in enumerate(results):
        result['score'] = 1 / (i + 1) + keyword_score
    return sorted(results, key=lambda x: x['score'], reverse=True)

# api_clients.py
def get_google_results(query):
    return [{'title': 'Google Result', 'url': 'https://google.com'}]

def get_bing_results(query):
    return [{'title': 'Bing Result', 'url': 'https://bing.com'}]

def get_yahoo_results(query):
    return [{'title': 'Yahoo Result', 'url': 'https://yahoo.com'}]

def get_all_results(query):
    return get_google_results(query) + get_bing_results(query) + get_yahoo_results(query)

from flask import Flask, render_template, request

from api_clients import get_all_results
from db import save_query_results
from ranking import rank_results

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form['query']
        api_results = get_all_results(query)
        ranked = rank_results(query, api_results)
        save_query_results(query, ranked)
        results = ranked
    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)


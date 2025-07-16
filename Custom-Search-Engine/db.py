import sqlite3


def get_connection():
    return sqlite3.connect("custom_search.db")

def save_query_results(query, results):
    conn = get_connection()
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            title TEXT,
            url TEXT
        )
    """)

    for res in results:
        cursor.execute(
            "INSERT INTO search_results (query, title, url) VALUES (?, ?, ?)",
            (query, res['title'], res['url'])
        )

    conn.commit()
    conn.close()

# db.py
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",            # ← Update with your MySQL username
        password="yourpassword",# ← Update with your MySQL password
        database="custom_search"
    )

def save_query_results(query, results):
    conn = get_connection()
    cursor = conn.cursor()
    for res in results:
        cursor.execute(
            "INSERT INTO search_results (query, title, url) VALUES (%s, %s, %s)",
            (query, res['title'], res['url'])
        )
    conn.commit()
    conn.close()

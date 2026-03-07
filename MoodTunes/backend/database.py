import sqlite3
import os


def get_db():
    # BDD locale SQLite stockée dans le dossier backend
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

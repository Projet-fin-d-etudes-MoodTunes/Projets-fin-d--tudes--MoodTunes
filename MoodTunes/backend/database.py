import sqlite3
import os


def get_db():
    # DB locale SQLite stockee dans le dossier backend
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    conn = sqlite3.connect(db_path)
    # Permet d'acceder aux colonnes par nom (row["id"]) au lieu d'index
    conn.row_factory = sqlite3.Row
    return conn

import sqlite3
import os


def get_db():
    """
    Ouvre une connexion SQLite partagée par les scripts backend.
    Cette fonction centralise le chemin de la DB et le format des lignes
    pour garder un acces coherent dans tout le projet.
    """
    # DB locale SQLite stockee dans le dossier backend
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    conn = sqlite3.connect(db_path)
    # Permet d'acceder aux colonnes par nom (row["id"]) au lieu d'index
    conn.row_factory = sqlite3.Row
    return conn

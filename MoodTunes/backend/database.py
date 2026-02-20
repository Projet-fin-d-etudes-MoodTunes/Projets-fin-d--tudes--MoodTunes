import sqlite3
import os


def get_db():
    print("DB PATH:", os.path.abspath("users.db"))
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

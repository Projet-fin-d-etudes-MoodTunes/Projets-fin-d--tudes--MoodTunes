from database import get_db

# Script one-shot pour creer les tables et index de base
# Il sert surtout a l'initialisation locale du projet.
# IMPORTANT !!!!!!
# CECI EST LA BASE DE DONNÉE DE BASE AVANT DE NOMBNREUX AJOUTS. ILS ONT ÉTÉ FAIT DIRECTEMENT SUR LA BASE DE DONNÉES POUR AMÉLIORER LE PROJET
# CONSULTER LE FICHIER BDDExport.sql POUR CONSULTER LA BASE DE DONNÉES COMPLÈTE AVEC SES CHANGEMENTS
db = get_db()
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    genres TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spotify_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    artist TEXT NOT NULL,
    embed_url TEXT NOT NULL,
    emotion TEXT NOT NULL,
    genre TEXT NOT NULL,          
    playlist_id TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    emotion TEXT NOT NULL,
    liked INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
)
""")

# Index utilisés par les routes de recommandation et historique pour permettre aux requêtes d'être plus vite
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_tracks_emotion_genre ON tracks(emotion, genre)")
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_history(user_id)")
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_user_history_user_liked ON user_history(user_id, liked)")

db.commit()
db.close()

print("Base de données créée ✅")

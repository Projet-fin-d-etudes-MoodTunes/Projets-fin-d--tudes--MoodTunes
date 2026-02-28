from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import requests
import base64
from dotenv import load_dotenv
from train_model import train_model_for_user
from database import get_db
import random
import joblib
import pandas as pd

load_dotenv()

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

ACCESS_TOKEN = os.getenv("SPOTIFY_TOKEN")


# ===============================
# Spotify Login
# ===============================
@app.route("/spotify/login")
def spotify_login():
    scope = "playlist-read-private playlist-read-collaborative"

    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}"
        f"&scope={scope}"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
    )

    return redirect(auth_url)


# ===============================
# Spotify Callback
# ===============================
@app.route("/spotify/callback")
def spotify_callback():
    global ACCESS_TOKEN

    code = request.args.get("code")

    url = "https://accounts.spotify.com/api/token"

    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }

    response = requests.post(url, headers=headers, data=data)
    json_result = response.json()

    ACCESS_TOKEN = json_result.get("access_token")

    return jsonify({
        "message": "Spotify connecté avec succès ✅",
        "access_token": ACCESS_TOKEN
    })


# ===============================
# Signup
# ===============================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    genres = data.get("genres", [])

    if not username or not password:
        return jsonify({"error": "Champs manquants"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, genres) VALUES (?, ?, ?)",
            (
                username,
                generate_password_hash(password),
                json.dumps(genres)
            )
        )
        db.commit()
    except:
        return jsonify({"error": "Utilisateur existe déjà"}), 400
    finally:
        db.close()

    return jsonify({"username": username, "genres": genres}), 201


# ===============================
# Login
# ===============================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    db.close()

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Mot de passe incorrect"}), 401

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "genres": json.loads(user["genres"])
    })

# ===============================
# RECOMMENDATION
# ===============================


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_id = data.get("user_id")
    emotion = data.get("emotion")

    if not user_id or not emotion:
        return jsonify({"error": "Missing data"}), 400

    db = get_db()
    cursor = db.cursor()

    #  Récupérer genres utilisateur
    cursor.execute("SELECT genres FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        db.close()
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user_genres = json.loads(user["genres"])
    placeholders = ",".join(["?"] * len(user_genres))

    # Filtrage de base
    query = f"""
        SELECT *
        FROM tracks
        WHERE emotion = ?
        AND genre IN ({placeholders})
        AND energy >= 0
        AND valence >= 0
        AND danceability >= 0
        AND acousticness >= 0
        AND instrumentalness >= 0
        AND speechiness >= 0
        AND tempo >= 0
        AND id NOT IN (
            SELECT track_id
            FROM user_history
            WHERE user_id = ? AND liked = 0
        )
        AND id NOT IN (
            SELECT track_id
            FROM user_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        )
        ORDER BY RANDOM()
        LIMIT 200
    """

    params = [emotion] + user_genres + [user_id, user_id]
    cursor.execute(query, params)
    candidates = cursor.fetchall()

    EMOTION_PROFILES = {
        "heureux": {"energy_min": 0.6, "valence_min": 0.6},
        "calme": {"energy_max": 0.4},
        "triste": {"valence_max": 0.4},
        "energique": {"energy_min": 0.75},
        "amour": {"valence_min": 0.4, "energy_max": 0.7}
    }

    profile = EMOTION_PROFILES.get(emotion, {})

    filtered_candidates = []

    for track in candidates:
        valid = True

        if "energy_min" in profile and track["energy"] < profile["energy_min"]:
            valid = False
        if "energy_max" in profile and track["energy"] > profile["energy_max"]:
            valid = False
        if "valence_min" in profile and track["valence"] < profile["valence_min"]:
            valid = False
        if "valence_max" in profile and track["valence"] > profile["valence_max"]:
            valid = False

        if valid:
            filtered_candidates.append(track)

    # fallback si trop strict
    if not filtered_candidates:
        filtered_candidates = candidates

    candidates = filtered_candidates

    if not candidates:
        db.close()
        return jsonify({"error": "Aucune musique trouvée"}), 404

    # Charger modèle
    model_path = f"../user_model_{user_id}.pkl"

    if not os.path.exists(model_path):
        chosen = random.choice(candidates)
        db.close()
        return jsonify({
            "track_id": chosen["id"],
            "spotify_id": chosen["spotify_id"],
            "name": chosen["name"],
            "artist": chosen["artist"],
            "embed_url": chosen["embed_url"]
        })

    model = joblib.load(model_path)

    FEATURE_COLUMNS = [
        "energy",
        "valence",
        "danceability",
        "acousticness",
        "instrumentalness",
        "speechiness",
        "tempo",
        "loudness"
    ]

    # Construire DataFrame candidats
    df_candidates = pd.DataFrame(candidates)

    # Supprimer lignes invalides
    df_candidates = df_candidates.dropna(subset=FEATURE_COLUMNS)

    if df_candidates.empty:
        chosen = random.choice(candidates)
        db.close()
        return jsonify({
            "track_id": chosen["id"],
            "spotify_id": chosen["spotify_id"],
            "name": chosen["name"],
            "artist": chosen["artist"],
            "embed_url": chosen["embed_url"]
        })

    X_candidates = df_candidates[FEATURE_COLUMNS]

    # Calcul probabilité ML
    probabilities = model.predict_proba(X_candidates)[:, 1]

    df_candidates["score"] = probabilities

    # Trier par score décroissant
    df_candidates = df_candidates.sort_values(by="score", ascending=False)

    # Top 30
    top_n = df_candidates.head(30)

    print(df_candidates[["name", "score"]].head(10))

    # Random parmi top
    chosen = top_n.sample(1).iloc[0]

    db.close()

    return jsonify({
        "track_id": int(chosen["id"]),
        "spotify_id": chosen["spotify_id"],
        "name": chosen["name"],
        "artist": chosen["artist"],
        "embed_url": chosen["embed_url"]
    })
# ===============================
# Vote du user
# ===============================


@app.route("/vote", methods=["POST"])
def vote():
    data = request.json

    user_id = data.get("user_id")
    track_id = data.get("track_id")
    emotion = data.get("emotion")
    liked = data.get("liked")

    if user_id is None or track_id is None or emotion is None or liked is None:
        return jsonify({"error": "Missing data"}), 400

    db = get_db()
    cursor = db.cursor()

    # Sauvegarder vote
    cursor.execute("""
        INSERT INTO user_history (user_id, track_id, emotion, liked)
        VALUES (?, ?, ?, ?)
    """, (user_id, track_id, emotion, liked))

    db.commit()

    # Compter interactions
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM user_history
        WHERE user_id = ?
    """, (user_id,))

    total = cursor.fetchone()["total"]

    db.close()

    # Retrain batch de 10
    if total % 10 == 0 and total >= 20:
        print(f"🔁 Retraining model for user {user_id} (total={total})")
        train_model_for_user(user_id)

    return jsonify({"message": "Vote saved"})


# ===============================
# Musiques sauvegardées
# ===============================
@app.route("/saved/<int:user_id>", methods=["GET"])
def get_saved_tracks(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT 
            t.id,
            t.spotify_id,
            t.name,
            t.artist,
            t.embed_url,
            MAX(h.timestamp) as last_liked
        FROM user_history h
        JOIN tracks t ON h.track_id = t.id
        WHERE h.user_id = ?
        AND h.liked = 1
        GROUP BY t.id
        ORDER BY last_liked DESC
    """, (user_id,))

    tracks = cursor.fetchall()
    db.close()

    return jsonify([
        {
            "track_id": track["id"],
            "spotify_id": track["spotify_id"],
            "name": track["name"],
            "artist": track["artist"],
            "embed_url": track["embed_url"]
        }
        for track in tracks
    ])


if __name__ == "__main__":
    app.run(debug=True)

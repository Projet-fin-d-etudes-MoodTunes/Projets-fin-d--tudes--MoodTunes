from flask import Flask, request, jsonify, redirect, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import requests
import base64
import sqlite3
import logging
import time
import hmac
import hashlib
from dotenv import load_dotenv
from train_model import train_model_for_user
from database import get_db
import random
import joblib
import pandas as pd
from functools import wraps

load_dotenv()

app = Flask(__name__)
# On lit les origines qui sont autorisées dans .env pour le CORS
allowed_origins = os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173").split(",")
allowed_origins = [origin.strip()
                   for origin in allowed_origins if origin.strip()]
CORS(app, resources={r"/*": {"origins": allowed_origins}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
# Sert a signer les tokens d'authentification
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
# Durée de vie du token en secondes
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", str(7 * 24 * 60 * 60)))

if JWT_SECRET == "change-me-in-production":
    logger.warning(
        "JWT_SECRET is using the default value. Set JWT_SECRET in environment for deployment.")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Chemin pour trouver le modèle de l'utilisateur


def get_model_path(user_id):
    return os.path.join(MODEL_DIR, f"user_model_{user_id}.pkl")


def _b64url_encode(data_bytes):
    return base64.urlsafe_b64encode(data_bytes).rstrip(b"=").decode("utf-8")


def _b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

# Création d'un JWT associé à un ID


def create_jwt(user_id):
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())

    payload = {"sub": int(user_id), "iat": now, "exp": now + JWT_EXP_SECONDS}

    header_b64 = _b64url_encode(json.dumps(
        header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(
        payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET.encode("utf-8"),
                         signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_signature = hmac.new(JWT_SECRET.encode(
            "utf-8"), signing_input, hashlib.sha256).digest()
        actual_signature = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_signature, actual_signature):
            raise ValueError("Invalid signature")

        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        exp = payload.get("exp")
        sub = payload.get("sub")

        # ID utilisateur valide + token pas expiré
        if not isinstance(sub, int):
            raise ValueError("Invalid subject")
        if not isinstance(exp, int) or exp < int(time.time()):
            raise ValueError("Token expired")

        return payload
    except Exception as exc:
        raise ValueError("Invalid token") from exc

# Fonction de sécurité pour les routes Flask


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"error": "Missing token"}), 401

        try:
            payload = decode_jwt(token)
            # On stocke l'id auth dans g pour l'utiliser dans la route
            g.auth_user_id = int(payload["sub"])
        except ValueError:
            return jsonify({"error": "Invalid token"}), 401

        return fn(*args, **kwargs)

    return wrapper


# Spotify Login
# Fonction et route qui permet la connexion à mon compte Spotify pour obtenir les playlists
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


# Spotify Callback
# Fonction et route qui permet de recevoir le token pour faire le lien entre l'API et le code
@app.route("/spotify/callback")
def spotify_callback():
    # Code OAuth renvoyé par Spotify apres la connexion
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

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
    # Déboggage pour savoir si l'autentification a marché
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        json_result = response.json()
    except requests.RequestException:
        return jsonify({"error": "Spotify auth request failed"}), 502

    if not json_result.get("access_token"):
        return jsonify({"error": "Spotify token missing"}), 502

    return jsonify({
        "message": "Spotify connection successful"
    })


# Signup
# Fonction et route dans laquelle le user est créé en gardant en donné son username, son id, son passwrod et les genres de musiques aiméees
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
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
                # Mot de passe sécurisé
                generate_password_hash(password),
                json.dumps(genres)
            )
        )
        user_id = cursor.lastrowid
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Utilisateur existe déjà"}), 400
    except sqlite3.DatabaseError:
        return jsonify({"error": "Database error"}), 500
    finally:
        db.close()

    token = create_jwt(user_id)
    return jsonify({"id": user_id, "username": username, "genres": genres, "token": token}), 201


# Login
# Fonction et route dans laquelle on regarde dans la base de données si le user et le mot de passse match les inputs du user
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
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

    # Nouveau token a chaque connexion par raison de sécurité
    token = create_jwt(user["id"])

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "genres": json.loads(user["genres"]),
        "token": token
    })

# Recommandation
# Fonction et route de recommandation de musiques


@app.route("/recommend", methods=["POST"])
@require_auth
def recommend():
    data = request.json or {}

    # On récupère le user id et l'émotion sélectionnée
    user_id = g.auth_user_id
    emotion = data.get("emotion")

    if not user_id or not emotion:
        return jsonify({"error": "Missing data"}), 400
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user_id"}), 400

    db = get_db()
    cursor = db.cursor()

    # On récupère les genres aimées par le user
    cursor.execute("SELECT genres FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        db.close()
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user_genres = json.loads(user["genres"])
    placeholders = ",".join(["?"] * len(user_genres))

    # Filtrage de base:
    # 1. emotion + genres aimées par le user
    # 2. on exclut les musiques sans features (-1)
    # 3. on exclut les dislikes et les musiques qui ont été recommandées parmi les 10 dernières
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

    # On fait un deuxième filtre par la suite pour que les musiques respectent tout de même un minimum l'émotion sélectionné si il y a une musique mise par accident dans une playlist
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

    # On garde la liste initiale si aucune musique respecte les critères
    if not filtered_candidates:
        filtered_candidates = candidates

    candidates = filtered_candidates

    if not candidates:
        db.close()
        return jsonify({"error": "Aucune musique trouvée"}), 404

    # On charge le modèle ML si le user en a un
    model_path = get_model_path(user_id)

    # Sinon on prend une musiques au hasard parmi les candidats
    if not os.path.exists(model_path):
        # Si le modele n'existe pas encore, on retourne un choix aleatoire
        chosen = random.choice(candidates)
        db.close()
        return jsonify({
            "track_id": chosen["id"],
            "spotify_id": chosen["spotify_id"],
            "name": chosen["name"],
            "artist": chosen["artist"],
            "embed_url": chosen["embed_url"]
        })

    try:
        model = joblib.load(model_path)
    except Exception:

        logger.warning(
            "Model load failed for user_id=%s. Falling back to random recommendation.", user_id)
        chosen = random.choice(candidates)
        db.close()
        return jsonify({
            "track_id": chosen["id"],
            "spotify_id": chosen["spotify_id"],
            "name": chosen["name"],
            "artist": chosen["artist"],
            "embed_url": chosen["embed_url"]
        })

    # Ordre et liste des audio features
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

    # On construit un DataFrame pour pouvoir utiliser les données
    df_candidates = pd.DataFrame([dict(row) for row in candidates])

    # On regarde que chaque musique ait toutes les colonnes nécessaires
    missing_features = [
        col for col in FEATURE_COLUMNS if col not in df_candidates.columns]
    if missing_features:
        logger.warning(
            "Missing feature columns for user_id=%s: %s. Falling back to random recommendation.",
            user_id,
            ",".join(missing_features),
        )
        chosen = random.choice(candidates)
        db.close()
        return jsonify({
            "track_id": chosen["id"],
            "spotify_id": chosen["spotify_id"],
            "name": chosen["name"],
            "artist": chosen["artist"],
            "embed_url": chosen["embed_url"]
        })

    # On supprime les musiques qui manque des données
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

    # Construcion du X pour le modèle
    X_candidates = df_candidates[FEATURE_COLUMNS]

    # Il renvoie les musiques que l'utilisateur aimerais ou pas et on chosit celle qu'il aimerait
    probabilities = model.predict_proba(X_candidates)[:, 1]

    # Chaque musique obtient un score de probabilité
    df_candidates["score"] = probabilities

    # Trier en décroissant
    df_candidates = df_candidates.sort_values(by="score", ascending=False)

    # On choisit les 30 meilleures
    top_n = df_candidates.head(30)

    logger.debug("Top candidate scores computed for user_id=%s", user_id)

    # On choisit une musique aléatoire parmi le top 30
    chosen = top_n.sample(1).iloc[0]

    db.close()

    return jsonify({
        "track_id": int(chosen["id"]),
        "spotify_id": chosen["spotify_id"],
        "name": chosen["name"],
        "artist": chosen["artist"],
        "embed_url": chosen["embed_url"]
    })

# Vote du user
# Fonction et route qui permet le vote sur une musique


@app.route("/vote", methods=["POST"])
@require_auth
def vote():
    data = request.json or {}

    # On obtient le user et musique id pour pouvoir associé l'opinion à celle ci
    user_id = g.auth_user_id
    track_id = data.get("track_id")
    emotion = data.get("emotion")
    liked = data.get("liked")

    if track_id is None or emotion is None or liked is None:
        return jsonify({"error": "Missing data"}), 400
    try:
        track_id = int(track_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid track_id"}), 400

    db = get_db()
    cursor = db.cursor()

    # On sauvegarde le vote dans la BDD
    cursor.execute("""
        INSERT INTO user_history (user_id, track_id, emotion, liked)
        VALUES (?, ?, ?, ?)
    """, (user_id, track_id, emotion, liked))

    db.commit()

    # On compte les intéractions pour pouvoir entraîner le ML modèle
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM user_history
        WHERE user_id = ?
    """, (user_id,))

    total = cursor.fetchone()["total"]

    db.close()

    # On re entraine le modèle après chaque 10 intéraction et il faut un minimum de 20 intéractions pour pouvoir l'entrainer
    if total % 10 == 0 and total >= 20:
        logger.info("Retraining model for user %s (total=%s)", user_id, total)
        train_model_for_user(user_id)

    return jsonify({"message": "Vote saved"})


# Musiques sauvegardées
# Fonction et route pour pouvoir avoir accès aux musiques aimées (sauvegardées)
@app.route("/saved/<int:user_id>", methods=["GET"])
@require_auth
def get_saved_tracks(user_id):
    # Mesure de sécurité, on peut juste voir ses propres liked
    if g.auth_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

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

    # On retourne les informations nécessaires pour pouvoir afficher chaque musiques liked
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


# Update user preferences
# Fonction et route pour pouvoir modifier les préférences musicales du user
@app.route("/preferences", methods=["PUT"])
@require_auth
def update_preferences():
    data = request.json or {}
    # On obtient l'ID à travers le token de connexion JWT
    user_id = g.auth_user_id
    genres = data.get("genres")

    if not genres:
        return jsonify({"error": "Missing data"}), 400

    db = get_db()
    cursor = db.cursor()

    # On met à jour dans la BDD
    cursor.execute("""
        UPDATE users
        SET genres = ?
        WHERE id = ?
    """, (json.dumps(genres), user_id))

    db.commit()
    db.close()

    return jsonify({
        "message": "Préférences mises à jour",
        "genres": genres
    })


if __name__ == "__main__":
    flask_debug = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=flask_debug)

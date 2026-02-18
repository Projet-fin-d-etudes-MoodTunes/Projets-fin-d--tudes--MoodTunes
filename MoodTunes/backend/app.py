from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import requests
import base64
from dotenv import load_dotenv
from database import get_db

load_dotenv()

app = Flask(__name__)
CORS(app)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

spotify_access_token = None  # stocké temporairement


# ===============================
# 🔐 Spotify Login
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
# 🔐 Spotify Callback
# ===============================
@app.route("/spotify/callback")
def spotify_callback():
    global spotify_access_token

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

    spotify_access_token = json_result.get("access_token")

    return jsonify({
        "message": "Spotify connecté avec succès ✅",
        "access_token": spotify_access_token
    })


# ===============================
# 👤 Signup
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
# 👤 Login
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


if __name__ == "__main__":
    app.run(debug=True)

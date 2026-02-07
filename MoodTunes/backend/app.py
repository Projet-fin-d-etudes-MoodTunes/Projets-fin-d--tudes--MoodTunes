from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Permet au front React de communiquer avec le backend

# Stockage temporaire en mémoire (dictionnaire)
users = {}

# ===========================
# Endpoint pour créer un compte
# ===========================


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    genres = data.get("genres", [])

    # Vérifications simples
    if not username or not password:
        return jsonify({"error": "Champs manquants"}), 400

    if username in users:
        return jsonify({"error": "Utilisateur existe déjà"}), 400

    # Création du compte
    users[username] = {
        "password": generate_password_hash(password),
        "genres": genres
    }

    # Retourne l'utilisateur créé
    return jsonify({"username": username, "genres": genres}), 201


# ===========================
# Endpoint pour se connecter
# ===========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Mot de passe incorrect"}), 401

    return jsonify({
        "username": username,
        "genres": user["genres"]
    })


# ===========================
# Endpoint pour lister les utilisateurs (facultatif)
# ===========================
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)


if __name__ == "__main__":
    app.run(debug=True)

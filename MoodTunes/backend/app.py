from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = {}

@app.route("/create-user", methods=["POST"])

def create_user():
    data = request.json
    username = data["username"]
    genres = data["genres"]

    if username in users:
        return jsonify({"error": "Utilisateur existe déjà"}), 400
    
    users[username] = genres
    return jsonify({"message": "Utilisateur créé", "user":data})


@app.route("/users", methods=["GET"])

def get_users():
    return jsonify(users)


if __name__ == "__main__":
    app.run(debug=True)


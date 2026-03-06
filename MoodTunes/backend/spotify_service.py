import os
from dotenv import load_dotenv
import requests
import base64
import time

load_dotenv()

# Variables Spotify chargees depuis .env
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("SPOTIFY_TOKEN")


def get_access_token():
    """
    Demande un token Spotify via Client Credentials.
    Utilise surtout pour les scripts de seed (pas pour des actions utilisateur).
    """
    # Token app-level (client credentials), utile pour les scripts de seed
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    result = requests.post(url, headers=headers, data=data, timeout=10)
    result.raise_for_status()
    json_result = result.json()
    return json_result["access_token"]


def fetch_playlist_tracks(playlist_id):
    """
    Recupere toutes les tracks d'une playlist Spotify.
    - Requete paginee (champ `next` de Spotify)
    - Gestion basique du rate-limit HTTP 429
    - Retourne une liste normalisee prete a inserer dans la DB
    """
    # Recupere les tracks d'une playlist Spotify en paginant sur "next"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items?limit=100"
    token = ACCESS_TOKEN or get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    tracks = []
    while url:
        # Tant que Spotify fournit une URL "next", on continue la pagination.
        try:
            result = requests.get(url, headers=headers, timeout=15)
        except requests.RequestException as e:
            print("Network error:", e)
            break
        print("Status:", result.status_code)

        if result.status_code == 429:
            # Spotify limite le debit, on attend le temps recommande
            retry_after = int(result.headers.get("Retry-After", 5))
            print(f"⏳ Rate limit atteint. Attente {retry_after} secondes...")
            time.sleep(retry_after)
            continue

        if result.status_code != 200:
            print("❌ Erreur:", result.status_code, result.text)
            break

        data = result.json()

        for item in data["items"]:
            track = item.get("item")

            if track and track["type"] == "track":
                # Format commun attendu par seed_tracks.py
                tracks.append({
                    "spotify_id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "embed_url": f"https://open.spotify.com/embed/track/{track['id']}"
                })

        url = data.get("next")
        # 20 secondes de pause entre CHAQUE requête
        time.sleep(20)

    print("Nombre de tracks récupérés :", len(tracks))

    return tracks

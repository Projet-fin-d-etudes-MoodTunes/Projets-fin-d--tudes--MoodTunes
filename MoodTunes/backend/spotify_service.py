import os
from dotenv import load_dotenv
import requests
import base64
import time

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("SPOTIFY_TOKEN")


def get_access_token():
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

    result = requests.post(url, headers=headers, data=data)
    json_result = result.json()
    return json_result["access_token"]


def fetch_playlist_tracks(playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items?limit=100"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    tracks = []
    while url:
        result = requests.get(url, headers=headers)
        print("Status:", result.status_code)

        if result.status_code == 429:
            retry_after = int(result.headers.get("Retry-After", 5))
            print(f"⏳ Rate limit atteint. Attente {retry_after} secondes...")
            time.sleep(retry_after)
            continue

        if result.status_code != 200:
            print("❌ Erreur:", result.status_code, result.text)
            break

        data = result.json()

        for item in data.get("items", []):
            track = item.get("track")

            if track and track.get("id"):
                tracks.append({
                    "spotify_id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "embed_url": f"https://open.spotify.com/embed/track/{track['id']}"
                })

        url = data.get("next")

    return tracks

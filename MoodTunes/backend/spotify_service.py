import os
from dotenv import load_dotenv
import requests
import base64

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


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


def fetch_playlist_tracks(playlist_id, access_token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    tracks = []
    while url:
        result = requests.get(url, headers=headers)
        data = result.json()

        for item in data["items"]:
            track = item.get("track")
            if track:
                tracks.append({
                    "spotify_id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "embed_url": f"https://open.spotify.com/embed/track/{track['id']}"
                })

        url = data.get("next")

    return tracks

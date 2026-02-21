from database import get_db
import requests
import time

BASE_URL = "https://api.reccobeats.com/v1"
DELAY_SECONDS = 1


# ==========================================
# Obtenir le Reccobeats ID depuis Spotify ID
# ==========================================
def get_reccobeats_id(spotify_id):
    url = f"{BASE_URL}/track?ids={spotify_id}"

    try:
        response = requests.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"⏳ Rate limit lookup. Attente {retry_after}s")
            time.sleep(retry_after)
            return get_reccobeats_id(spotify_id)

        if response.status_code != 200:
            print("❌ Lookup error:", response.status_code, response.text)
            return None

        data = response.json()

        if "content" not in data or not data["content"]:
            return None

        return data["content"][0]["id"]

    except Exception as e:
        print("Erreur lookup:", e)
        return None


# ==========================================
# Récupérer audio features via Recco ID
# ==========================================
def fetch_audio_features(recco_id):
    url = f"{BASE_URL}/track/{recco_id}/audio-features"

    try:
        response = requests.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"⏳ Rate limit audio. Attente {retry_after}s")
            time.sleep(retry_after)
            return fetch_audio_features(recco_id)

        if response.status_code != 200:
            print("❌ Audio error:", response.status_code, response.text)
            return None

        return response.json()

    except Exception as e:
        print("Erreur audio:", e)
        return None


# ==========================================
# Update base de données
# ==========================================
def update_track(track_id, features):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE tracks
        SET energy = ?,
            valence = ?,
            tempo = ?,
            danceability = ?,
            acousticness = ?,
            instrumentalness = ?,
            loudness = ?,
            speechiness = ?
        WHERE id = ?
    """, (
        features.get("energy"),
        features.get("valence"),
        features.get("tempo"),
        features.get("danceability"),
        features.get("acousticness"),
        features.get("instrumentalness"),
        features.get("loudness"),
        features.get("speechiness"),
        track_id
    ))

    db.commit()
    db.close()


# ==========================================
# Script principal
# ==========================================
def main():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, spotify_id
        FROM tracks
        WHERE energy IS NULL
    """)

    tracks = cursor.fetchall()
    db.close()

    print(f"\n🎵 {len(tracks)} tracks à traiter\n")

    for i, track in enumerate(tracks):
        print(f"[{i+1}/{len(tracks)}] Spotify ID: {track['spotify_id']}")

        recco_id = get_reccobeats_id(track["spotify_id"])

        if not recco_id:
            print("❌ Recco ID non trouvé\n")
            update_track(track["id"], {
                "energy": -1,
                "valence": -1,
                "tempo": -1,
                "danceability": -1,
                "acousticness": -1,
                "instrumentalness": -1,
                "loudness": -1,
                "speechiness": -1
            })
            continue

        print("Recco ID:", recco_id)

        features = fetch_audio_features(recco_id)

        if features:
            update_track(track["id"], features)
            print("✅ Updated\n")
        else:
            print("❌ Audio features non trouvées\n")

        time.sleep(DELAY_SECONDS)

    print("🏁 Terminé")


if __name__ == "__main__":
    main()

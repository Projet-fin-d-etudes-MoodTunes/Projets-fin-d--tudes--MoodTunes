from database import get_db
from playlist_config import PLAYLISTS
from spotify_service import fetch_playlist_tracks
import time


def save_tracks(tracks, emotion, genre, playlist_id):
    db = get_db()
    cursor = db.cursor()

    for track in tracks:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tracks
                (spotify_id, name, artist, embed_url, emotion, genre, playlist_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                track["spotify_id"],
                track["name"],
                track["artist"],
                track["embed_url"],
                emotion,
                genre,
                playlist_id
            ))
        except Exception as e:
            print("Erreur insertion:", e)

    db.commit()
    db.close()


def main():

    START_INDEX = 11  # playlist 12 (index commence à 0)
    # for i, playlist in enumerate(PLAYLISTS):
    #     print(f"[{i+1}/{len(PLAYLISTS)}] ➡️ Import playlist {playlist['playlist_id']} | {playlist['emotion']} | {playlist['genre']}")
    # for i, playlist in enumerate(PLAYLISTS[:2]):
    #     print(f"[{i+1}/1] ➡️ Import playlist {playlist['playlist_id']} | {playlist['emotion']} | {playlist['genre']}")
    for i, playlist in enumerate(PLAYLISTS[START_INDEX:], start=START_INDEX):
        print(f"[{i+1}/{len(PLAYLISTS)}] ➡️ Import playlist {playlist['playlist_id']} | {playlist['emotion']} | {playlist['genre']}")

        tracks = fetch_playlist_tracks(playlist["playlist_id"])
        print("Nombre de tracks récupérés :", len(tracks))

        save_tracks(
            tracks,
            playlist["emotion"],
            playlist["genre"],
            playlist["playlist_id"]
        )

        # Pause entre chaque playlist
        print("⏳ Pause 10 secondes...")
        time.sleep(10)

    print("✅ Import terminé")


if __name__ == "__main__":
    main()

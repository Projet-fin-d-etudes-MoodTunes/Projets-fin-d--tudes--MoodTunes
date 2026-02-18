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
    # for i, playlist in enumerate(PLAYLISTS):
    #     print(f"[{i+1}/{len(PLAYLISTS)}] ➡️ Import playlist {playlist['playlist_id']} | {playlist['emotion']} | {playlist['genre']}")
    for i, playlist in enumerate(PLAYLISTS[:1]):
        print(f"[{i+1}/1] ➡️ Import playlist {playlist['playlist_id']} | {playlist['emotion']} | {playlist['genre']}")

        tracks = fetch_playlist_tracks(playlist["playlist_id"])

        save_tracks(
            tracks,
            playlist["emotion"],
            playlist["genre"],
            playlist["playlist_id"]
        )

        # Pause entre chaque playlist
        print("⏳ Pause 7 secondes...")
        time.sleep(7)

    print("✅ Import terminé")


if __name__ == "__main__":
    main()

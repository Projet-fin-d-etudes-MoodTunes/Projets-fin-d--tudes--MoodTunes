from database import get_db
from playlist_config import PLAYLISTS
from spotify_service import get_access_token, fetch_playlist_tracks


def save_tracks(tracks, emotion, genre, playlist_id):
    db = get_db()
    cursor = db.cursor()

    for track in tracks:
        cursor.execute("""
            INSERT OR IGNORE INTO tracks
            (spotify_id, name, artist, embed_url, emotion, playlist_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track["spotify_id"],
            track["name"],
            track["artist"],
            track["embed_url"],
            emotion,
            playlist_id
        ))

    db.commit()
    db.close()


def main():
    token = get_access_token()

    for playlist in PLAYLISTS:
        tracks = fetch_playlist_tracks(playlist["playlist_id"], token)
        save_tracks(
            tracks,
            playlist["emotion"],
            playlist["genre"],
            playlist["playlist_id"]
        )

    print("✅ Import terminé")


if __name__ == "__main__":
    main()

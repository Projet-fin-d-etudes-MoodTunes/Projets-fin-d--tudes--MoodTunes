import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";
import { AuthContext } from "../AuthContext";
import "./styles/Saved.css";

export default function Saved() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  useEffect(() => {
    if (!user?.id) return;

    fetch(`http://localhost:5000/saved/${user.id}`)
      .then(res => res.json())
      .then(data => {
        setTracks(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Erreur chargement saved:", err);
        setLoading(false);
      });
  }, [user]);

  return (
    <AppShell onLogout={handleLogout}>
      <div className="saved-root">
        <h1 className="saved-title">Musiques sauvegardées</h1>

        {loading && <p>Chargement...</p>}

        {!loading && tracks.length === 0 && (
          <p>Aucune musique aimée pour le moment.</p>
        )}

        <div className="saved-grid">
            {tracks.map((track, index) => (
              <div
                key={track.track_id}
                className="saved-card"
                style={{ animationDelay: `${index * 0.08}s` }}
              >
              <div className="saved-track-title">
                {track.name} — {track.artist}
              </div>

              <iframe
                title={track.spotify_id}
                src={track.embed_url}
                width="100%"
                height="152"
                frameBorder="0"
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"
              />
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
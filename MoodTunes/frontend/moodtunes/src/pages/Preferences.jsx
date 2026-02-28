import { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import AppShell from "../components/AppShell";
import "./styles/Preferences.css";

const GENRES = [
  { id: "pop", label: "Pop", includes: ["Indie Pop", "Dance Pop"] },
  { id: "rock", label: "Rock", includes: ["Alternative Rock", "Metal"] },
  { id: "rap", label: "Rap", includes: ["Hip-Hop", "Trap"] },
  { id: "rnb", label: "R&B / Soul", includes: ["Neo Soul", "Soul"] },
  { id: "electronique", label: "Electronique", includes: ["House", "EDM"] },
  { id: "chill", label: "Chill", includes: ["Lo-fi", "Ambient", "Jazz"] },
];

export default function Preferences() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const [selectedGenres, setSelectedGenres] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (user?.genres) {
      setSelectedGenres(user.genres);
    }
  }, [user]);

  const handleGenreChange = (genreId) => {
    setSelectedGenres((prev) =>
      prev.includes(genreId)
        ? prev.filter((g) => g !== genreId)
        : [...prev, genreId]
    );
  };

  const handleSave = async () => {
    if (selectedGenres.length === 0) {
      setMessage("Sélectionne au moins un genre");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:5000/preferences", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          genres: selectedGenres,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.error || "Erreur");
        return;
      }

      const updatedUser = {
        ...user,
        genres: selectedGenres,
      };

      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));

      setMessage("Préférences mises à jour ✅");
    } catch {
      setMessage("Erreur serveur");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <AppShell onLogout={handleLogout}>
      <div className="preferences-root">
        <div className="preferences-card">
          <h1>Préférences musicales</h1>

          <div className="preferences-genres">
            {GENRES.map((genre) => (
              <div key={genre.id} className="preferences-genre-group">
                <label className="preferences-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedGenres.includes(genre.id)}
                    onChange={() => handleGenreChange(genre.id)}
                  />
                  <span>{genre.label}</span>
                </label>

                <div className="preferences-subgenres">
                  Inclus : {genre.includes.join(", ")}
                </div>
              </div>
            ))}
          </div>

          {message && <p className="preferences-message">{message}</p>}

          <button
            className="preferences-button"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? "Enregistrement..." : "Sauvegarder"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}
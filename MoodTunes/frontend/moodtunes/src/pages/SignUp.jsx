import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import "../styles/Auth.css";

/**
 * Genres principaux seulement.
 * Les sous-genres sont informatifs.
 * On stocke uniquement le `id`.
 */
const GENRES = [
  { id: "pop", label: "Pop", includes: ["Indie Pop", "Dance Pop"] },
  { id: "rock", label: "Rock", includes: ["Alternative Rock", "Metal"] },
  { id: "rap", label: "Rap", includes: ["Hip-Hop", "Trap"] },
  { id: "rnb", label: "R&B / Soul", includes: ["Neo Soul", "Soul"] },
  { id: "electronique", label: "Electronique", includes: ["House", "EDM"] },
  { id: "chill", label: "Chill", includes: ["Lo-fi", "Ambient", "Jazz"] },
];

function SignUp() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleGenreChange = (genreId) => {
    setSelectedGenres((prev) =>
      prev.includes(genreId)
        ? prev.filter((g) => g !== genreId)
        : [...prev, genreId]
    );
  };

  const handleSubmit = async () => {
    setError("");

    if (!username || !password) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    if (selectedGenres.length === 0) {
      setError("Veuillez sélectionner au moins un genre");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          password,
          genres: selectedGenres,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.error || "Erreur lors de la création du compte");
        return;
      }

      setUser({
        id: data.id,
        username: data.username,
        genres: data.genres,
      });

      localStorage.setItem(
        "user",
        JSON.stringify({
          id: data.id,
          username: data.username,
          genres: data.genres,
        })
      );

      navigate("/home");
    } catch {
      setError("Impossible de créer le compte. Vérifie le serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Créer un compte</h1>
          <p>
            Sélectionne tes genres favoris.  
            Les sous-genres sont inclus automatiquement.
          </p>
        </div>

        <div className="auth-form">
          <label className="auth-label">
            Nom d’utilisateur
            <input
              className="auth-input"
              placeholder="MoodTunesEnjoyer"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </label>

          <label className="auth-label">
            Mot de passe
            <input
              className="auth-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </label>

          <div className="auth-genres">
            <h2 className="auth-genres-title">Genres favoris</h2>

            {GENRES.map((genre) => (
              <div key={genre.id} className="auth-genre-group">
                <label className="auth-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedGenres.includes(genre.id)}
                    onChange={() => handleGenreChange(genre.id)}
                  />
                  <span>{genre.label}</span>
                </label>

                <div className="auth-subgenres">
                  Inclus : {genre.includes.join(", ")}
                </div>
              </div>
            ))}
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-button"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Création..." : "Créer le compte"}
          </button>
        </div>

        <div className="auth-alt-actions">
          <button
            type="button"
            className="auth-secondary"
            onClick={() => navigate("/signin")}
          >
            J’ai déjà un compte
          </button>

          <Link className="auth-back" to="/">
            ← Retour à l’accueil
          </Link>
        </div>
      </div>
    </div>
  );
}

export default SignUp;

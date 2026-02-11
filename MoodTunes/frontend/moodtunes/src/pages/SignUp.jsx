import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import "./styles/Auth.css";

const GENRES = {
  Pop: ["Pop", "Indie Pop", "Electro Pop"],
  Rock: ["Rock", "Alternative Rock", "Metal"],
  Urban: ["Hip-Hop", "Rap", "R&B", "Funk"],
  Chill: ["Jazz", "Lo-fi", "Ambient"],
};

function SignUp() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleGenreChange = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
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
        body: JSON.stringify({ username, password, genres: selectedGenres }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.error || "Erreur lors de la création du compte");
        return;
      }

      setUser({ username: data.username, genres: data.genres });
      localStorage.setItem(
        "user",
        JSON.stringify({ username: data.username, genres: data.genres })
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
          <p>Choisis tes goûts musicaux pour des recommandations plus précises.</p>
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
            <div className="auth-genres-title">Goûts musicaux</div>

            {Object.entries(GENRES).map(([category, genres]) => (
              <div key={category} className="auth-genre-group">
                <div className="auth-genre-category">{category}</div>

                {genres.map((genre) => (
                  <label key={genre} className="auth-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedGenres.includes(genre)}
                      onChange={() => handleGenreChange(genre)}
                    />
                    <span>{genre}</span>
                  </label>
                ))}
              </div>
            ))}
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-button" onClick={handleSubmit} disabled={loading}>
            {loading ? "Création..." : "Créer le compte"}
          </button>
        </div>

        <div className="auth-footer">
          <Link className="auth-link" to="/">
            ← Retour à l’accueil
          </Link>
          <span className="auth-sep">•</span>
          <Link className="auth-link" to="/signin">
            J’ai déjà un compte
          </Link>
        </div>
      </div>
    </div>
  );
}

export default SignUp;

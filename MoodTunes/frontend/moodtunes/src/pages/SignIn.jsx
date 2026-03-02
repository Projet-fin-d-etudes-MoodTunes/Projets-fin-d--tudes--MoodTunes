import { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import "../styles/Auth.css";

function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.error || "Erreur de connexion");
        return;
      }

      setUser({
        id: data.id,
        username: data.username,
        genres: data.genres,
      });

      localStorage.setItem(
        "user",
        JSON.stringify({ id: data.id, 
                          username: data.username, 
                          genres: data.genres 
                        })
      );

      navigate("/home");
    } catch {
      setError("Impossible de se connecter. Vérifie le serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Connexion</h1>
          <p>Reprenez votre univers musical.</p>
        </div>

        <div className="auth-form">
          <label className="auth-label">
            Nom d’utilisateur
            <input
              className="auth-input"
              placeholder="MoodTunesEnjoyer"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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
            />
          </label>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-button"
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </div>

        <div className="auth-alt-actions">
          <button
            type="button"
            className="auth-secondary"
            onClick={() => navigate("/signup")}
          >
            Créer un compte
          </button>

          <Link className="auth-back" to="/">
            ← Retour à l’accueil
          </Link>
        </div>
      </div>
    </div>
  );
}

export default SignIn;

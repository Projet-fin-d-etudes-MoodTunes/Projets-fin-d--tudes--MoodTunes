import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";

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

  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleGenreChange = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre)
        ? prev.filter((g) => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSubmit = async () => {
    // ✅ validations simples
    if (!username || !password) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    if (selectedGenres.length === 0) {
      setError("Veuillez sélectionner au moins un genre");
      return;
    }

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
      setError(data.error);
      return;
    }

    // ✅ compte créé → utilisateur connecté
    setUser({
      username: data.username,
      genres: data.genres
    });

    localStorage.setItem(
      "user",
      JSON.stringify({
        username: data.username,
        genres: data.genres
      })
    );

    localStorage.setItem(
      "user",
      JSON.stringify({ username: data.username })
    );
    navigate("/home");
  };

  return (
    <div style={{ padding: "1.5rem" }}>
      <h1>Créer un compte</h1>

      <input
        placeholder="Nom d'utilisateur"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "100%" }}
      />

      <input
        type="password"
        placeholder="Mot de passe"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "100%" }}
      />

      <h3>Choisis tes goûts musicaux</h3>

      {Object.entries(GENRES).map(([category, genres]) => (
        <div key={category} style={{ marginBottom: "1rem" }}>
          <strong>{category}</strong>
          {genres.map((genre) => (
            <label key={genre} style={{ display: "block" }}>
              <input
                type="checkbox"
                checked={selectedGenres.includes(genre)}
                onChange={() => handleGenreChange(genre)}
              />
              {genre}
            </label>
          ))}
        </div>
      ))}

      <button onClick={handleSubmit}>Créer le compte</button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default SignUp;

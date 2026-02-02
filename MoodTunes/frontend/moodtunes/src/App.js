import { useState } from "react";

const GENRES = {
  Pop: ["Pop", "Indie Pop", "Electro Pop"],
  Rock: ["Rock", "Alternative Rock", "Metal"],
  Urban: ["Hip-Hop", "Rap", "R&B", "Funk"],
  Chill: ["Jazz", "Lo-fi", "Ambient"],
  Languages: ["English", "French", "Spanish", "Korean", "Japanese", "Portugese", "Arabic"]
};

function App() {
  const [username, setUsername] = useState("");
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [message, setMessage] = useState("");

  const handleGenreChange = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre)
        ? prev.filter((g) => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSubmit = async () => {
    const response = await fetch("http://localhost:5000/create-user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        genres: selectedGenres
      })
    });

    const data = await response.json();
    setMessage(data.message || data.error);
  };

  return (
    <div>
      <h1>MoodTunes</h1>

      <input
        placeholder="Nom d'utilisateur"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <h3>Choisis tes goûts musicaux</h3>

      {Object.entries(GENRES).map(([category, genres]) => (
        <div key={category}>
          <h4>{category}</h4>
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

      <br />

      <button onClick={handleSubmit}>Créer profil</button>

      <p>{message}</p>

      <p>
        <strong>Genres sélectionnés :</strong>{" "}
        {selectedGenres.join(", ")}
      </p>
    </div>
  );
}

export default App;

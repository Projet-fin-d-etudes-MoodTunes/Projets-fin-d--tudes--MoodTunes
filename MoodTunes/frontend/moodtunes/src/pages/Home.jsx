import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";

function Home() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div>
      <h1>Bienvenue {user?.username} 🎧</h1>

      <h3>Tes préférences musicales :</h3>

      {user?.genres && user.genres.length > 0 ? (
        <ul>
          {user.genres.map((genre) => (
            <li key={genre}>{genre}</li>
          ))}
        </ul>
      ) : (
        <p>Aucune préférence enregistrée</p>
      )}

      <button onClick={handleLogout}>
        Déconnexion
      </button>
    </div>
  );
}

export default Home;

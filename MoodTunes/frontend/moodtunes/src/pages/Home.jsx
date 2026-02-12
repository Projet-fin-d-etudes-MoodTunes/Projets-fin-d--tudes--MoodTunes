import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import FloatingLines from '../components/FloatingLines';

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
      <div style={{ width: '100%', height: '600px', position: 'relative' }}>
        <FloatingLines 
          enabledWaves={["top","middle","bottom"]}
          // Array - specify line count per wave; Number - same count for all waves
          lineCount={6}
          // Array - specify line distance per wave; Number - same distance for all waves
          lineDistance={5}
          bendRadius={5}
          bendStrength={-0.5}
          interactive={true}
          parallax={true}
        />
      </div>
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

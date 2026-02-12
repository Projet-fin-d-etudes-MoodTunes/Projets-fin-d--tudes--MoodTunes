import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import FloatingLines from "../components/FloatingLines";
import "./styles/Home.css";

function Home() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="home-root">
      <div className="floating-bg">
        <FloatingLines
          enabledWaves={["top", "middle", "bottom"]}
          lineCount={6}
          lineDistance={5}
          bendRadius={5}
          bendStrength={-0.5}
          interactive={true}
          parallax={true}
        />
      </div>

      <div className="home-content">
        <h1>Bienvenue {user?.username} 🎧</h1>

        <h3>Tes préférences musicales :</h3>

        {user?.genres?.length ? (
          <ul>
            {user.genres.map((g) => (
              <li key={g}>{g}</li>
            ))}
          </ul>
        ) : (
          <p>Aucune préférence enregistrée</p>
        )}

        <button onClick={handleLogout}>Déconnexion</button>
      </div>
    </div>
  );
}

export default Home;

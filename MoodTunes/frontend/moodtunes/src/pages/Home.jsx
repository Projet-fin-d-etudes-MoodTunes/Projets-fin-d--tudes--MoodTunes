import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import AppShell from "../components/AppShell";
import FloatingLines from "../components/FloatingLines";
import "./styles/Home.css";

export default function Home() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <AppShell onLogout={handleLogout}>
      <div className="home-root">
        <div className="floating-bg" aria-hidden="true">
          <FloatingLines
            enabledWaves={["top","middle","bottom"]}
            lineCount={6}
            lineDistance={5}
            bendRadius={5}
            bendStrength={-0.5}
            parallax={true}
            animationSpeed={0.9}
            mixBlendMode="screen"
            linesGradient={["#363742", "#7160a5", "#457287"]}
          />
        </div>

        <div className="home-content">
          <h1>Bienvenue {user?.username} 🎧</h1>
          <h2>Quelle émotion sens-tu aujourd’hui ?</h2>
          <p>Je te recommanderai une musique.</p>
        </div>
      </div>
    </AppShell>
  );
}

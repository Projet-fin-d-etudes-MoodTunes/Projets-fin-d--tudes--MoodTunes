// src/pages/Home.jsx
import { useContext, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import AppShell from "../components/AppShell";
import FloatingLines from "../components/FloatingLines";
import "./styles/Home.css";

// THEME DE BASE (par défaut / refresh)
const BASE_GRADIENT = ["#363742", "#7160a5", "#457287"];

const EMOTIONS = [
  {
    id: "base",
    label: "Base",
    energy: "Neutre",
    movementLabel: "Doux",
    sensation: "Clair",
    gradient: BASE_GRADIENT,

    animationSpeed: 0.9,
    waveAmp: 0.25,
    waveFreq: 0.9,
    waveThickness: 0.016,

    bendStrength: -0.45,
    parallaxStrength: 0.18,
    lineDistance: 5,
    lineCount: 6,
  },

  {
    id: "heureux",
    label: "Heureux",
    energy: "Élevée",
    movementLabel: "Ondulations",
    sensation: "Joyeuses",
    gradient: ["#DFD8A1", "#FFBF76", "#C7F6F3"],

    // ULTRA vivant / beaucoup de vagues / assez épaisses
    animationSpeed: 2.1,
    waveAmp: 0.75,
    waveFreq: 2.2,
    waveThickness: 0.030,

    bendStrength: -1.35,
    parallaxStrength: 0.48,
    lineDistance: 2,
    lineCount: 12,
  },

  {
    id: "calme",
    label: "Calme",
    energy: "Basse",
    movementLabel: "Très lent",
    sensation: "Apaisant",
    gradient: ["#A1E8FB", "#DAF5BF", "#F1B6F2"],

    // GRANDES vagues très lentes (calme = lent + large)
    animationSpeed: 0.42,
    waveAmp: 0.95,
    waveFreq: 0.28,
    waveThickness: 0.034,

    bendStrength: -0.12,
    parallaxStrength: 0.06,
    lineDistance: 11,
    lineCount: 4,
  },

  {
    id: "amour",
    label: "Amour",
    energy: "Moyenne-basse",
    movementLabel: "Enveloppant",
    sensation: "Chaleureux",
    gradient: ["#FFB5D0", "#FED0A8", "#FF4D5F"],

    // “Enveloppant” = très rond, lent-moyen, épais, fréquence basse
    animationSpeed: 0.85,
    waveAmp: 0.70,
    waveFreq: 0.55,
    waveThickness: 0.032,

    bendStrength: -0.65,
    parallaxStrength: 0.22,
    lineDistance: 3,
    lineCount: 9,
  },

  {
    id: "triste",
    label: "Triste",
    energy: "Basse",
    movementLabel: "Diffus",
    sensation: "Lourd",
    gradient: ["#0B1020", "#1F2A44", "#4B7BBF"],

    // Diffus/lourd = très lent + faible amplitude + très basse fréquence + lignes très espacées + très fines
    animationSpeed: 0.30,
    waveAmp: 0.10,
    waveFreq: 0.18,
    waveThickness: 0.0075,

    bendStrength: -0.06,
    parallaxStrength: 0.03,
    lineDistance: 14,
    lineCount: 3,
  },

  {
    id: "energique",
    label: "Énergique",
    energy: "Élevée",
    movementLabel: "Rapide",
    sensation: "Dynamique",
    gradient: ["#C3070A", "#CC7930", "#19C919"],

    // Très nerveux = très rapide + fréquence très haute + amplitude moyenne + très fin + plein de lignes
    animationSpeed: 2.4,
    waveAmp: 0.40,
    waveFreq: 3.0,
    waveThickness: 0.010,

    bendStrength: -1.6,
    parallaxStrength: 0.60,
    lineDistance: 2,
    lineCount: 14,
  },
];

export default function Home() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  // ✅ par défaut (refresh) = thème de base = Base
  const [emotionId, setEmotionId] = useState("base");

  const active = useMemo(
    () => EMOTIONS.find((e) => e.id === emotionId) || EMOTIONS[1],
    [emotionId]
  );

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
            enabledWaves={["top", "middle", "bottom"]}
            lineCount={active.lineCount}
            lineDistance={active.lineDistance}
            bendRadius={5}
            bendStrength={active.bendStrength}
            mouseDamping={0.05}
            interactive={true}
            parallax={true}
            parallaxStrength={active.parallaxStrength}
            animationSpeed={active.animationSpeed}
            mixBlendMode="screen"
            linesGradient={active.gradient}
            waveAmp={active.waveAmp}
            waveFreq={active.waveFreq}
            waveThickness={active.waveThickness}
          />
        </div>

        <div className="home-content">
          <h1>Bienvenue {user?.username} 🎧</h1>
          <h2>Quelle émotion sens-tu aujourd’hui ?</h2>
          <p>Choisis une émotion pour adapter l’ambiance.</p>

          <div className="emotion-grid">
            {EMOTIONS.map((e) => (
              <button
                key={e.id}
                type="button"
                className={`emotion-card ${emotionId === e.id ? "is-active" : ""}`}
                onClick={() => setEmotionId(e.id)}
              >
                <div className="emotion-title">{e.label}</div>
                <div className="emotion-meta">
                  <span>{e.energy}</span>
                  <span>•</span>
                  <span>{e.movementLabel}</span>
                </div>
                <div className="emotion-sense">{e.sensation}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

// src/pages/Home.jsx
import { useContext, useMemo, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import AppShell from "../components/AppShell";
import FloatingLines from "../components/FloatingLines";
import "./styles/Home.css";

// THEME DE BASE (par défaut / refresh)
const BASE_GRADIENT = ["#363742", "#7160a5", "#457287"];

// Spotify embeds
const EMOTION_TRACKS = {
  heureux: {
    title: "MoodTunes — Heureux",
    artist: "À définir",
    embedUrl:
      "https://open.spotify.com/embed/track/60nZcImufyMA1MKQY3dcCH?utm_source=generator",
  },
  calme: {
    title: "MoodTunes — Calme",
    artist: "À définir",
    embedUrl:
      "https://open.spotify.com/embed/track/0oufSLnKQDoBFX5mgkDCgR?utm_source=generator",
  },
  amour: {
    title: "MoodTunes — Amour",
    artist: "À définir",
    embedUrl:
      "https://open.spotify.com/embed/track/3DZQ6mzUkAdHqZWzqxBKIK?utm_source=generator",
  },
  triste: {
    title: "MoodTunes — Triste",
    artist: "À définir",
    embedUrl:
      "https://open.spotify.com/embed/track/047fCsbO4NdmwCBn8pcUXl?utm_source=generator",
  },
  energique: {
    title: "MoodTunes — Énergique",
    artist: "À définir",
    embedUrl:
      "https://open.spotify.com/embed/track/1BIXs6CdkPRLytuqoXs6XN?utm_source=generator",
  },
};

const EMOTIONS = [
  {
    id: "base",
    label: "Base",
    energy: "Neutre",
    movementLabel: "Doux",
    sensation: "Clair",
    gradient: BASE_GRADIENT,
    animationSpeed: 0.9,
    bendStrength: -0.5,
    parallaxStrength: 0.2,
    lineDistance: 5,
    lineCount: 6,
    waveAmp: 0.25,
    waveFreq: 0.9,
    waveThickness: 0.016,
  },
  {
    id: "heureux",
    label: "Heureux",
    energy: "Élevée",
    movementLabel: "Ondulations",
    sensation: "Joyeuses",
    gradient: ["#9d934c", "#9d6b33", "#2d5b58"],
    animationSpeed: 2.6,
    bendStrength: -1.35,
    parallaxStrength: 0.48,
    lineDistance: 2,
    lineCount: 12,
    waveAmp: 0.75,
    waveFreq: 2.2,
    waveThickness: 0.03,
  },
  {
    id: "calme",
    label: "Calme",
    energy: "Basse",
    movementLabel: "Très lent",
    sensation: "Apaisant",
    gradient: ["#A1E8FB", "#DAF5BF", "#F1B6F2"],
    animationSpeed: 0.42,
    bendStrength: -0.12,
    parallaxStrength: 0.06,
    lineDistance: 11,
    lineCount: 4,
    waveAmp: 0.95,
    waveFreq: 0.28,
    waveThickness: 0.034,
  },
  {
    id: "amour",
    label: "Amour",
    energy: "Moyenne-basse",
    movementLabel: "Enveloppant",
    sensation: "Chaleureux",
    gradient: ["#FFB5D0", "#FED0A8", "#FF4D5F"],
    animationSpeed: 0.85,
    bendStrength: -0.65,
    parallaxStrength: 0.22,
    lineDistance: 3,
    lineCount: 9,
    waveAmp: 0.7,
    waveFreq: 0.55,
    waveThickness: 0.032,
  },
  {
    id: "triste",
    label: "Triste",
    energy: "Basse",
    movementLabel: "Diffus",
    sensation: "Lourd",
    gradient: ["#0B1020", "#1F2A44", "#4B7BBF"],
    animationSpeed: 0.3,
    bendStrength: -0.06,
    parallaxStrength: 0.03,
    lineDistance: 14,
    lineCount: 3,
    waveAmp: 0.1,
    waveFreq: 0.18,
    waveThickness: 0.0075,
  },
  {
    id: "energique",
    label: "Énergique",
    energy: "Élevée",
    movementLabel: "Rapide",
    sensation: "Dynamique",
    gradient: ["#C3070A", "#CC7930", "#19C919"],
    animationSpeed: 3.4,
    bendStrength: -1.6,
    parallaxStrength: 0.6,
    lineDistance: 2,
    lineCount: 14,
    waveAmp: 0.4,
    waveFreq: 3.0,
    waveThickness: 0.01,
  },
];

function getFeedbackKey(username) {
  return `moodtunes_feedback_v1__${username || "guest"}`;
}

export default function Home() {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const [screen, setScreen] = useState("choose");
  const [emotionId, setEmotionId] = useState("base");
  const [feedback, setFeedback] = useState({});

  // animations
  const [mounted, setMounted] = useState(false);
  const [transitioning, setTransitioning] = useState(false);

  const active = useMemo(
    () => EMOTIONS.find((e) => e.id === emotionId) || EMOTIONS[0],
    [emotionId]
  );

  const activeTrack = EMOTION_TRACKS[emotionId] || null;

  // 
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  // Charger feedback au mount + quand user change
  useEffect(() => {
    const key = getFeedbackKey(user?.username);
    const raw = localStorage.getItem(key);
    setFeedback(raw ? JSON.parse(raw) : {});
  }, [user?.username]);

  const persistFeedback = (next) => {
    const key = getFeedbackKey(user?.username);
    localStorage.setItem(key, JSON.stringify(next));
    setUser((prev) => (prev ? { ...prev, feedback: next } : prev));
  };

  // Transition screen (fade-out -> switch -> fade-in)
  const goToScreen = useCallback((nextScreen) => {
    setTransitioning(true);
    window.setTimeout(() => {
      setScreen(nextScreen);
      setTransitioning(false);
    }, 220); 
  }, []);

  const handleChooseEmotion = (id) => {
    setEmotionId(id);
    goToScreen("player");
  };

  const handleVote = (liked) => {
    if (!activeTrack) {
      goToScreen("choose");
      return;
    }

    const entry = {
      liked,
      embedUrl: activeTrack.embedUrl,
      title: activeTrack.title,
      artist: activeTrack.artist,
      ts: Date.now(),
    };

    const next = { ...feedback, [emotionId]: entry };
    setFeedback(next);
    persistFeedback(next);

    // Après avis, retour automatique au choix (avec animation)
    window.setTimeout(() => {
      goToScreen("choose");
      // remettre le thème base après avis 
      // setEmotionId("base");
    }, 300);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/");
  };

  const CHOOSABLE_EMOTIONS = useMemo(
    () => EMOTIONS.filter((e) => e.id !== "base"),
    []
  );

  const getOverlayOpacity = (id) => {
    const map = {
      base: 0.4,
      heureux: 0.55,   // très lumineux → on assombrit plus
      calme: 0.45,
      amour: 0.5,
      triste: 0.35,    // déjà sombre → moins d’overlay
      energique: 0.6,  // rouge/vert très agressif
    };

    return map[id] ?? 0.5;
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
        <div
          className="ui-overlay"
          style={{
            background: `rgba(0,0,0,${getOverlayOpacity(emotionId)})`,
          }}
        />
        {/* ✅ animation container */}
        <div
          className={[
            "home-content",
            mounted ? "is-mounted" : "",
            transitioning ? "is-transitioning" : "",
          ].join(" ")}
        >
          {screen === "choose" ? (
            <>
              <h1>Bienvenue {user?.username} 🎧</h1>
              <h2>Quelle émotion sens-tu aujourd’hui ?</h2>
              <p>Choisis une émotion pour adapter l’ambiance.</p>

              <div className="emotion-grid">
                {CHOOSABLE_EMOTIONS.map((e) => (
                  <button
                    key={e.id}
                    type="button"
                    className="emotion-card"
                    onClick={() => handleChooseEmotion(e.id)}
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
            </>
          ) : (
            <>
              <div className="player-top">
                <div className="player-title">
                  <div className="player-emotion">{active.label}</div>
                  <div className="player-sub">
                    Je vous recommande{" "}
                    {activeTrack?.title || "une musique"} • de{" "}
                    {activeTrack?.artist || "..." }
                  </div>
                </div>
              </div>

              <div className="spotify-card">
                <iframe
                  title={`Spotify-${emotionId}`}
                  src={activeTrack?.embedUrl}
                  width="100%"
                  height="152"
                  frameBorder="0"
                  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                  loading="lazy"
                />
              </div>

              <div className="vote-row">
                <button
                  type="button"
                  className={`vote-btn like ${
                    feedback?.[emotionId]?.liked === true ? "is-active" : ""
                  }`}
                  onClick={() => handleVote(true)}
                >
                  J’aime
                </button>

                <button
                  type="button"
                  className={`vote-btn dislike ${
                    feedback?.[emotionId]?.liked === false ? "is-active" : ""
                  }`}
                  onClick={() => handleVote(false)}
                >
                  J’aime pas
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </AppShell>
  );
}

import { useNavigate } from "react-router-dom";
import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../AuthContext";
import TextType from "./scripts/TextType";
import "./styles/Landing.css";

function Landing() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  const [hovered, setHovered] = useState(null);
  const [colorIndex, setColorIndex] = useState(0);

  const colors = ["signin", "signup"];


  useEffect(() => {
    if (hovered) return;

    const interval = setInterval(() => {
      setColorIndex((prev) => (prev + 1) % colors.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [hovered]);


  useEffect(() => {
    if (user) navigate("/home");
  }, [user, navigate]);

  
  const activeBlock = hovered ?? colors[colorIndex];

  return (
    <div className="landing-page">
      <TextType
        text={["Bienvenue sur MoodTunes !"]}
        typingSpeed={75}
        deletingSpeed={50}
        pauseDuration={1500}
        showCursor
        cursorCharacter="_"
        variableSpeed={{ min: 60, max: 120 }}
        cursorBlinkDuration={0.5}
      />


      <div
        className={`button-block ${
          activeBlock === "signin" ? "active-bg" : "inactive-bg"
        }`}
        onMouseEnter={() => setHovered("signin")}
        onMouseLeave={() => setHovered(null)}
      >
        <h2>
          {activeBlock === "signin" ? "Bon retour !" : "Connectez-vous !"}
        </h2>
        <p>
          {activeBlock === "signin"
            ? "Prêt à écouter votre playlist ?"
            : "Reprenez où vous avez quitté !"}
        </p>
        <button onClick={() => navigate("/signin")}>
          Se connecter !
        </button>
      </div>

      <div
        className={`button-block ${
          activeBlock === "signup" ? "active-bg" : "inactive-bg"
        }`}
        onMouseEnter={() => setHovered("signup")}
        onMouseLeave={() => setHovered(null)}
      >
        <h2>
          {activeBlock === "signup" ? "Rejoignez-nous !" : "Pas de compte ?"}
        </h2>
        <p>
          {activeBlock === "signup"
            ? "Créez votre compte et découvrez de nouvelles musiques !"
            : "Découvrez de nouvelles musiques selon votre humeur !"}
        </p>
        <button onClick={() => navigate("/signup")}>
          Inscrivez-vous !
        </button>
      </div>
    </div>
  );
}

export default Landing;

// Landing.jsx (modifs: juste ajout de classes sur les boutons)
import { useNavigate } from "react-router-dom";
import { useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from "../AuthContext";
import TextType from "./scripts/TextType";
import { gsap } from "gsap";
import "./styles/Landing.css";

function Landing() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  const [introDone, setIntroDone] = useState(false);
  const overlayRef = useRef(null);
  const hasAnimatedOut = useRef(false);

  useEffect(() => {
    const t = setTimeout(() => {
      if (hasAnimatedOut.current) return;
      hasAnimatedOut.current = true;

      gsap.to(overlayRef.current, {
        yPercent: -100,
        duration: 1.1,
        ease: "power4.inOut",
        onComplete: () => setIntroDone(true),
      });
    }, 4730);

    return () => clearTimeout(t);
  }, []);

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
    <div className="landing-root">
      {!introDone && (
        <div ref={overlayRef} className="intro-overlay">
          <TextType
            text={["Bienvenue sur MoodTunes !"]}
            typingSpeed={75}
            deletingSpeed={50}
            pauseDuration={1500}
            showCursor
            cursorCharacter="_"
            variableSpeed={{ min: 60, max: 120 }}
            cursorBlinkDuration={0.5}
            loop={true}
            className="intro-title"
          />
        </div>
      )}

      <div className={`landing-page ${introDone ? "landing-show" : "landing-hide"}`}>
        <p className="landing-subtitle">
          Découvrez des musiques adaptées à vos goûts et à votre humeur.
        </p>
        <div
          className={`button-block ${
            activeBlock === "signin" ? "active-bg" : "inactive-bg"
          }`}
          onMouseEnter={() => setHovered("signin")}
          onMouseLeave={() => setHovered(null)}
        >
          <h2>{activeBlock === "signin" ? "Bon retour !" : "Connectez-vous !"}</h2>
          <p>
            {activeBlock === "signin"
              ? "Replongez dans votre univers musical."
              : "Reprenez où vous avez quitté !"}
          </p>

          {/* ✅ bouton qui alterne aussi (clair/foncé) */}
          <button
            className={`cta-button ${
              activeBlock === "signin" ? "btn-active" : "btn-inactive"
            }`}
            onClick={() => navigate("/signin")}
          >
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
          <h2>{activeBlock === "signup" ? "Rejoignez-nous !" : "Pas de compte ?"}</h2>
          <p>
            {activeBlock === "signup"
              ? "Créez votre compte et découvrez de nouvelles musiques !"
              : "Découvrez de nouvelles musiques selon votre humeur !"}
          </p>

          {/* ✅ bouton qui alterne aussi (clair/foncé) */}
          <button
            className={`cta-button ${
              activeBlock === "signup" ? "btn-active" : "btn-inactive"
            }`}
            onClick={() => navigate("/signup")}
          >
            Inscrivez-vous !
          </button>
        </div>
      </div>
    </div>
  );
}

export default Landing;

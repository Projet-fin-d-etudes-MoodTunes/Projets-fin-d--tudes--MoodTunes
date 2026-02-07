import { useNavigate } from "react-router-dom";

function Landing() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>MoodTunes</h1>
      <p>As-tu déjà un compte ?</p>

      <button onClick={() => navigate("/signin")}>
        Se connecter
      </button>

      <button onClick={() => navigate("/signup")}>
        Créer un compte
      </button>
    </div>
  );
}

export default Landing;

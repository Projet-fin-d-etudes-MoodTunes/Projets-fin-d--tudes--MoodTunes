import { useNavigate } from "react-router-dom";
import { useContext, useEffect } from "react";
import { AuthContext } from "../AuthContext";

function Landing() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  

  useEffect(() => {
    if (user) {
      navigate("/home");
    }
  }, [user, navigate]);

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

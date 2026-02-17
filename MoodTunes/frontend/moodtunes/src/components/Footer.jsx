import { useNavigate } from "react-router-dom";
import "../pages/styles/AppShell.css";

export default function Footer() {
  const navigate = useNavigate();

  const go = (e, path) => {
    e.preventDefault();
    navigate(path);
  };

  return (
    <footer className="app-footer">
      <a href="/about" className="footer-link" onClick={(e) => go(e, "/about")}>
        À propos
      </a>

      <a href="/saved" className="footer-link" onClick={(e) => go(e, "/saved")}>
        Musiques sauvegardées
      </a>

      <a href="/preferences" className="footer-link" onClick={(e) => go(e, "/preferences")}>
        Préférences
      </a>
    </footer>
  );
}

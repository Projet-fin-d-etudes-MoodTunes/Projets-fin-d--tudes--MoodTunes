import { useNavigate } from "react-router-dom";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import "../styles/AppShell.css";

export default function Footer() {
  const navigate = useNavigate();

  const go = (e, path) => {
    e.preventDefault();
    navigate(path);
  };

  return (
    <footer className="app-footer">
      <div className="footer-left">
        <a href="/home" className="footer-link" onClick={(e) => go(e, "/home")}>
          Accueil
        </a>

        <a href="/saved" className="footer-link" onClick={(e) => go(e, "/saved")}>
          Musiques sauvegardées
        </a>

        <a href="/preferences" className="footer-link" onClick={(e) => go(e, "/preferences")}>
          Préférences
        </a>
      </div>

      <div className="footer-right">
        <a
          href="https://github.com/perezerik"
          target="_blank"
          rel="noopener noreferrer"
          className="footer-icon"
        >
          <FaGithub />
        </a>

        <a
          href="https://www.linkedin.com/in/erik-perez-194605269/"
          target="_blank"
          rel="noopener noreferrer"
          className="footer-icon"
        >
          <FaLinkedin />
        </a>
      </div>
    </footer>
  );
}
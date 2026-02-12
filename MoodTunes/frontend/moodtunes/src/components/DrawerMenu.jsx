import { useNavigate } from "react-router-dom";
import "../pages/styles/AppShell.css";

export default function DrawerMenu({ open, onClose, onLogout }) {
  const navigate = useNavigate();

  const go = (e, path) => {
    e.preventDefault();   // empêche le reload
    onClose();
    navigate(path);
  };

  return (
    <div className={`drawer ${open ? "drawer-open" : ""}`} aria-hidden={!open}>
      <div className="drawer-panel">
        <button className="drawer-close" onClick={onClose} aria-label="Fermer">
          ×
        </button>

        <nav className="drawer-nav">
          <a href="/about" className="drawer-item" onClick={(e) => go(e, "/about")}>
            À propos
          </a>

          <a href="/saved" className="drawer-item" onClick={(e) => go(e, "/saved")}>
            Musiques sauvegardées
          </a>

          <a href="/preferences" className="drawer-item" onClick={(e) => go(e, "/preferences")}>
            Préférences
          </a>

          <button
            className="drawer-item drawer-logout"
            onClick={() => {
              onLogout();
              onClose();
            }}
          >
            Déconnexion
          </button>
        </nav>
      </div>

      <button className="drawer-backdrop" onClick={onClose} aria-label="Fermer le menu" />
    </div>
  );
}

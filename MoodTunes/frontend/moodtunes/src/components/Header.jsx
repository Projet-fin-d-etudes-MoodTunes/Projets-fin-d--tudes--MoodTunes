import { useState } from "react";
import DrawerMenu from "./DrawerMenu";
import "../styles/AppShell.css";

export default function Header({ onLogout }) {
  // Etat local du drawer mobile/desktop
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="app-header">
        <div className="app-brand">
          <a href="/home" className="app-brand">MoodTunes</a>
        </div>

        <button className="icon-btn" onClick={() => setOpen(true)} aria-label="Ouvrir le menu">
          <span className="burger" />
        </button>
      </header>

      {/* Le drawer recoit les callbacks de fermeture + logout depuis AppShell */}
      <DrawerMenu open={open} onClose={() => setOpen(false)} onLogout={onLogout} />
    </>
  );
}

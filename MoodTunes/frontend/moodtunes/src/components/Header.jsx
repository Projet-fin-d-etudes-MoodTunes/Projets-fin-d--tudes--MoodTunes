import { useState } from "react";
import DrawerMenu from "./DrawerMenu";
import "../styles/AppShell.css";

export default function Header({ onLogout }) {
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

      <DrawerMenu open={open} onClose={() => setOpen(false)} onLogout={onLogout} />
    </>
  );
}

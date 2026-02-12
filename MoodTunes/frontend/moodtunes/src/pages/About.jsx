import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";

export default function About() {
  const navigate = useNavigate();
  const onLogout = () => navigate("/"); // placeholder si tu veux

  return (
    <AppShell onLogout={onLogout}>
      <h1>À propos</h1>
      <p>MoodTunes recommande de la musique selon ton humeur.</p>
    </AppShell>
  );
}

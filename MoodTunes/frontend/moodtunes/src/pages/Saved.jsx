import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";

export default function Saved() {
  const navigate = useNavigate();
  const onLogout = () => navigate("/"); // placeholder

  return (
    <AppShell onLogout={onLogout}>
      <h1>Musiques sauvegardées</h1>
      <p>Liste à venir.</p>
    </AppShell>
  );
}

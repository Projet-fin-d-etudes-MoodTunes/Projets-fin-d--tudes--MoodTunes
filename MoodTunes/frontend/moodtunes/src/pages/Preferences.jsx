import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";

export default function Preferences() {
  const navigate = useNavigate();
  const onLogout = () => navigate("/"); // placeholder

  return (
    <AppShell onLogout={onLogout}>
      <h1>Préférences</h1>
      <p>Préférences à venir.</p>
    </AppShell>
  );
}

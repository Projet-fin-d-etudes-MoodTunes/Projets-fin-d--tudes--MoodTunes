import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";

export default function Contact() {
  const navigate = useNavigate();
  const onLogout = () => navigate("/"); // placeholder

  return (
    <AppShell onLogout={onLogout}>
      <h1>Contact</h1>
      <p>Formulaire à venir.</p>
    </AppShell>
  );
}

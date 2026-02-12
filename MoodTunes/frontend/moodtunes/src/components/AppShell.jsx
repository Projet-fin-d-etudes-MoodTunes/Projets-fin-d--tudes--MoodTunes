import Header from "./Header";
import Footer from "./Footer";
import "../pages/styles/AppShell.css";

export default function AppShell({ children, onLogout }) {
  return (
    <div className="shell">
      <Header onLogout={onLogout} />
      <main className="shell-main">{children}</main>
      <Footer />
    </div>
  );
}

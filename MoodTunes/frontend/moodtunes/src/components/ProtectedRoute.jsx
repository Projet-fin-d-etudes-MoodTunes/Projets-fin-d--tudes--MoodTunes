import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";

function ProtectedRoute({ children }) {
  const { user, token } = useContext(AuthContext);

  // Double verification:
  // - user: infos de session cote UI
  // - token: preuve d'auth cote API
  // Si pas connecte, on renvoie vers la landing
  if (!user || !token) {
    return <Navigate to="/" />;
  }

  return children;
}

export default ProtectedRoute;

import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";

function ProtectedRoute({ children }) {
  const { user, token } = useContext(AuthContext);

  if (!user || !token) {
    return <Navigate to="/" />;
  }

  return children;
}

export default ProtectedRoute;

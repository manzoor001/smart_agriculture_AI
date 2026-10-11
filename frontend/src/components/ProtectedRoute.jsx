
import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import api from "../services/api";

export default function ProtectedRoute() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let active = true;

    async function verifyToken() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setStatus("unauthenticated");
        return;
      }

      try {
        await api.get("/auth/me");

        if (active) {
          setStatus("authenticated");
        }
      } catch {
        localStorage.removeItem("access_token");

        if (active) {
          setStatus("unauthenticated");
        }
      }
    }

    verifyToken();

    return () => {
      active = false;
    };
  }, []);

  if (status === "checking") {
    return <div className="auth-loading">Verifying your session...</div>;
  }

  if (status === "unauthenticated") {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

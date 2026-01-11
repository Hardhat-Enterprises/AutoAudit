import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, LogOut, User } from "lucide-react";
import { logout as apiLogout } from "../api/client";
import { useAuth } from "../context/AuthContext";
import "./AccountPage.css";

export default function AccountPage({ sidebarWidth = 220, isDarkMode = true }) {
  const navigate = useNavigate();
  const { user, token, logout: clearAuth } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const primaryLabel =
    user?.email || user?.username || user?.name || user?.id || "Signed in";

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);

    try {
      await apiLogout(token);
    } catch (error) {
      // Best-effort: even if API logout fails (network, already-expired token),
      // we still clear local auth so the user is signed out client-side.
      console.warn("Logout request failed; clearing local auth anyway:", error);
    } finally {
      clearAuth();
      navigate("/");
    }
  };

  return (
    <div
      className={`account-page ${isDarkMode ? "dark" : "light"}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: "margin-left 0.4s ease, width 0.4s ease",
      }}
    >
      <div className="account-container">
        <div className="page-header">
          <div className="header-content">
            <User size={24} />
            <div className="header-text">
              <h1>Account</h1>
              <p>Profile and user preferences.</p>
            </div>
          </div>
          <button
            type="button"
            className="toolbar-button danger"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? (
              <>
                <Loader2 size={16} className="spinning" />
                <span>Logging out...</span>
              </>
            ) : (
              <>
                <LogOut size={16} />
                <span>Log out</span>
              </>
            )}
          </button>
        </div>

        <div className="account-card">
          <h3>Profile</h3>
          <div className="account-meta">
            <div className="meta-item">
              <span className="meta-label">User</span>
              <span className="meta-value">{primaryLabel}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


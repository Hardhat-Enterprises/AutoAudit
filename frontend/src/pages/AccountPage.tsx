import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, LogOut, User } from "lucide-react";
import { logout as apiLogout } from "../api/client";
import { useAuth } from "../context/AuthContext";
//import "./AccountPage.css";

type AccountPageProps = {
  sidebarWidth?: number;
  isDarkMode?: boolean;
  onThemeToggle?: () => void;
};

type AuthUser = {
  email?: string | null;
  username?: string | null;
  name?: string | null;
  id?: string | number | null;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  logout: () => void;
};

export default function AccountPage({ sidebarWidth = 220, isDarkMode = true }: AccountPageProps) {
  const navigate = useNavigate();
  const { user, token, logout: clearAuth } = useAuth() as AuthContextValue;
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const primaryLabel =
    user?.email || user?.username || user?.name || (user?.id != null ? String(user.id) : null) || "Signed in";

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);

    try {
      await apiLogout(token);
    } catch (error) {
      console.warn("Logout request failed; clearing local auth anyway:", error);
    } finally {
      clearAuth();
      navigate("/");
    }
  };

  return (
    <>
      <div
        className={`min-h-screen p-6 ${isDarkMode ? "bg-gray-900 text-gray-50" : "bg-gray-50 text-gray-900"}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: "margin-left 0.4s ease, width 0.4s ease",
        }}
      >
        <div className="account-container flex flex-col gap-6 max-w-4xl mx-auto">
          {/* Page header */}
          <div className="page-header flex items-center justify-between">
            <div className="header-content flex items-center gap-4">
              <User size={24} className="text-teal-400" />
              <div className="header-text">
                <h1 className="text-2xl font-bold m-0">Account</h1>
                <p className="text-sm text-gray-500 m-0">Profile and user preferences.</p>
              </div>
            </div>

            <button
              type="button"
              className="flex items-center gap-2 text-red-600 hover:text-red-800"
              onClick={handleLogout}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
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

          {/* Account card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Profile</h3>
            <div className="flex flex-wrap gap-6 pt-2 border-t border-gray-200">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">User</span>
                <span className="text-sm font-medium text-gray-900">{primaryLabel}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

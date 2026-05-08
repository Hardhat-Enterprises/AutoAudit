import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, LogOut, User } from "lucide-react";
import { logout as apiLogout } from "../api/client";
import { useAuth } from "../context/AuthContext";

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

export default function AccountPage({
  sidebarWidth = 220,
  isDarkMode = true,
}: AccountPageProps) {
  const navigate = useNavigate();
  const { user, token, logout: clearAuth } =
    useAuth() as AuthContextValue;

  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const primaryLabel =
    user?.email ||
    user?.username ||
    user?.name ||
    (user?.id != null ? String(user.id) : null) ||
    "Signed in";

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);

    try {
      await apiLogout(token);
    } catch (error) {
      console.warn("Logout request failed:", error);
    } finally {
      clearAuth();
      navigate("/");
    }
  };

  return (
    <div
      className={`min-h-screen transition-all duration-300 ${
        isDarkMode ? "bg-slate-900 text-white" : "bg-gray-100 text-black"
      }`}
      style={{
  marginLeft: sidebarWidth ? `${sidebarWidth}px` : 0,
  width: sidebarWidth ? `calc(100% - ${sidebarWidth}px)` : "100%",
}}
    >
      <div className="p-4 pl-24 mx-auto max-w-4xl sm:p-6 sm:pl-6">
        {/* HEADER */}
        <div className="flex flex-col gap-4 items-start mb-8 sm:flex-row sm:justify-between sm:items-center">
          <div className="flex gap-3 items-center">
            <User size={24} />
            <div>
              <h1 className="text-2xl font-semibold">Account</h1>
              <p className="text-sm opacity-70">
                Profile and user preferences.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="flex gap-2 justify-center items-center py-2 px-4 w-full bg-red-600 rounded-lg transition sm:w-auto hover:bg-red-700 disabled:opacity-50"
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

        {/* PROFILE CARD (FIXES YOUR PR COMMENTS) */}
        <div className="p-6 rounded-xl border shadow-md border-slate-700 bg-secondary">
          <h3 className="text-lg font-semibold">Profile</h3>

          <hr className="my-4 border border-slate-600"/>

          <div className="space-y-3">
            <div className="flex flex-col">
              <span className="text-sm opacity-70">User</span>
              <span className="text-base font-medium">
                {primaryLabel}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
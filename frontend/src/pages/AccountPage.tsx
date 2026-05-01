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
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
      }}
    >
      <div className="max-w-4xl mx-auto p-6">
        {/* HEADER */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
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
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 transition disabled:opacity-50"
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
        <div className="p-6 rounded-xl border border-slate-700 bg-secondary shadow-md">
          <h3 className="text-lg font-semibold">Profile</h3>

          <hr className="border border-slate-600 my-4"/>

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
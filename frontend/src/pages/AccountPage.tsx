import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Loader2,
  LogOut,
  User,
  Eye,
  EyeOff,
  Pencil,
  Save,
  X,
} from "lucide-react";
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
  organization?: string | null;
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
  const { user, token, logout: clearAuth } = useAuth() as AuthContextValue;
  console.log("USER DATA:", user);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const [isEditingProfile, setIsEditingProfile] = useState(false);

  const [profileData, setProfileData] = useState({
    firstName: "",
    lastName: "",
    organization: "",
  });

  useEffect(() => {
    const fullName = user?.name ?? "";

    setProfileData({
      firstName: fullName ? fullName.split(" ")[0] : "",
      lastName: fullName ? fullName.split(" ").slice(1).join(" ") : "",
      organization: user?.organization ?? "",
    });
  }, [user]);

  const handleProfileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setProfileData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditProfile = () => {
    setIsEditingProfile(true);
  };

  const handleCancelProfileEdit = () => {
    setProfileData({
      firstName: user?.name?.split(" ")[0] || "",
      lastName: user?.name?.split(" ").slice(1).join(" ") || "",
      organization: user?.organization || "",
    });
    setIsEditingProfile(false);
  };

  const handleSaveProfile = () => {
    console.log("Profile data to save:", profileData);
    setIsEditingProfile(false);
  };

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
      console.warn("Logout request failed; clearing local auth anyway:", error);
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
        transition: "margin-left 0.4s ease, width 0.4s ease",
      }}
    >
      <div className="mx-auto max-w-6xl p-9">
        <div className="mb-8 flex items-center justify-between">
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
            className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
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

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-8 shadow-md">
          <div className="mb-6 flex items-center justify-between gap-3">
            <h3 className="text-2xl font-semibold">Profile</h3>

            {!isEditingProfile ? (
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-600 bg-slate-900 px-5 py-3 font-semibold text-white transition hover:opacity-90"
                onClick={handleEditProfile}
              >
                <Pencil size={16} />
                <span>Edit Profile</span>
              </button>
            ) : (
              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-600 bg-slate-900 px-5 py-3 font-semibold text-white transition hover:opacity-90"
                  onClick={handleCancelProfileEdit}
                >
                  <X size={16} />
                  <span>Cancel</span>
                </button>

                <button
                  type="button"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-300 px-5 py-3 font-semibold text-slate-950 transition hover:opacity-90"
                  onClick={handleSaveProfile}
                >
                  <Save size={16} />
                  <span>Save Changes</span>
                </button>
              </div>
            )}
          </div>

          {!isEditingProfile ? (
            <div className="grid grid-cols-1 gap-8 border-t border-slate-700 pt-4 sm:grid-cols-3">
              <div>
                <span className="block text-xs font-semibold uppercase tracking-widest text-slate-400">
                  Name
                </span>
                <span className="mt-2 block text-base font-semibold">
                  {user?.name
                    ? user.name
                    : user?.email
                      ? user.email.split("@")[0].replace(/\./g, " ")
                      : "Not available"}
                </span>
              </div>

              <div>
                <span className="block text-xs font-semibold uppercase tracking-widest text-slate-400">
                  Email
                </span>
                <span className="mt-2 block text-base font-semibold">
                  {user?.email || "Not available"}
                </span>
              </div>

              <div>
                <span className="block text-xs font-semibold uppercase tracking-widest text-slate-400">
                  Organization
                </span>
                <span className="mt-2 block text-base font-semibold">
                  {user?.organization || "AutoAudit"}
                </span>
              </div>
            </div>
          ) : (
            <div className="space-y-4 border-t border-slate-700 pt-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="firstName"
                    className="text-sm font-semibold text-slate-300"
                  >
                    First Name
                  </label>
                  <input
                    id="firstName"
                    name="firstName"
                    type="text"
                    value={profileData.firstName}
                    onChange={handleProfileChange}
                    placeholder="Enter first name"
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="lastName"
                    className="text-sm font-semibold text-slate-300"
                  >
                    Last Name
                  </label>
                  <input
                    id="lastName"
                    name="lastName"
                    type="text"
                    value={profileData.lastName}
                    onChange={handleProfileChange}
                    placeholder="Enter last name"
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label
                  htmlFor="organization"
                  className="text-sm font-semibold text-slate-300"
                >
                  Organization
                </label>
                <input
                  id="organization"
                  name="organization"
                  type="text"
                  value={profileData.organization}
                  onChange={handleProfileChange}
                  placeholder="Enter organization name"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                />
              </div>
            </div>
          )}
        </div>

        {/* Change Password Card */}

        <div className="mt-8 rounded-xl border border-slate-700 bg-slate-800 p-8 shadow-md">
          <h3 className="text-2xl font-semibold">Change Password</h3>

          <div className="mt-5 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <label
                htmlFor="currentPassword"
                className="text-sm font-semibold text-slate-300"
              >
                Current Password
              </label>
              <div className="relative flex items-center">
                <input
                  id="currentPassword"
                  name="currentPassword"
                  type={showCurrentPassword ? "text" : "password"}
                  placeholder="Enter current password"
                  value={passwordData.currentPassword}
                  onChange={handlePasswordChange}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 pr-10 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                />
                <button
                  type="button"
                  className="absolute right-3 text-slate-400 transition hover:text-cyan-300"
                  onClick={() => setShowCurrentPassword((prev) => !prev)}
                  aria-label={
                    showCurrentPassword
                      ? "Hide current password"
                      : "Show current password"
                  }
                >
                  {showCurrentPassword ? (
                    <EyeOff size={16} />
                  ) : (
                    <Eye size={16} />
                  )}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label
                htmlFor="newPassword"
                className="text-sm font-semibold text-slate-300"
              >
                New Password
              </label>
              <div className="relative flex items-center">
                <input
                  id="newPassword"
                  name="newPassword"
                  type={showNewPassword ? "text" : "password"}
                  placeholder="Enter new password"
                  value={passwordData.newPassword}
                  onChange={handlePasswordChange}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 pr-10 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                />
                <button
                  type="button"
                  className="absolute right-3 text-slate-400 transition hover:text-cyan-300"
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  aria-label={
                    showNewPassword ? "Hide new password" : "Show new password"
                  }
                >
                  {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label
                htmlFor="confirmPassword"
                className="text-sm font-semibold text-slate-300"
              >
                Confirm Password
              </label>
              <div className="relative flex items-center">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm new password"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 pr-10 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300"
                />
                <button
                  type="button"
                  className="absolute right-3 text-slate-400 transition hover:text-cyan-300"
                  onClick={() => setShowConfirmPassword((prev) => !prev)}
                  aria-label={
                    showConfirmPassword
                      ? "Hide confirm password"
                      : "Show confirm password"
                  }
                >
                  {showConfirmPassword ? (
                    <EyeOff size={16} />
                  ) : (
                    <Eye size={16} />
                  )}
                </button>
              </div>
            </div>

            <button
              type="button"
              className="mt-2 inline-flex w-fit items-center justify-center rounded-lg bg-cyan-300 px-5 py-3 font-semibold text-slate-950 transition hover:opacity-90"
            >
              Update Password
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

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

  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

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

  const inputClass = `w-full rounded-lg border px-3 py-2 text-sm outline-none transition
    ${
      isDarkMode
        ? "border-slate-700 bg-slate-900 text-white placeholder:text-slate-500 focus:border-cyan-300"
        : "border-gray-300 bg-white text-gray-900 placeholder:text-gray-400 focus:border-cyan-500"
    }`;

  const labelClass = `text-sm font-semibold ${
    isDarkMode ? "text-slate-300" : "text-gray-600"
  }`;

  const cardClass = `rounded-xl border p-6 shadow-md ${
    isDarkMode ? "border-slate-700 bg-slate-800" : "border-gray-200 bg-white"
  }`;

  const secondaryButtonClass = `inline-flex items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-semibold transition hover:opacity-90
    ${
      isDarkMode
        ? "border-slate-700 bg-slate-900 text-white"
        : "border-gray-300 bg-white text-gray-900"
    }`;

  const primaryButtonClass =
    "inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:opacity-90";

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setProfileData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCancelProfileEdit = () => {
    const fullName = user?.name ?? "";

    setProfileData({
      firstName: fullName ? fullName.split(" ")[0] : "",
      lastName: fullName ? fullName.split(" ").slice(1).join(" ") : "",
      organization: user?.organization ?? "",
    });

    setIsEditingProfile(false);
  };

  const handleSaveProfile = () => {
    console.log("Profile data to save:", profileData);
    setIsEditingProfile(false);
  };

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
      }}
    >
      <div className="mx-auto max-w-4xl p-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between gap-4">
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
            className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-50"
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

        <div className="space-y-6">
          {/* Profile Card */}
          <div className={cardClass}>
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="text-lg font-semibold">Profile</h3>

              {!isEditingProfile ? (
                <button
                  type="button"
                  className={secondaryButtonClass}
                  onClick={() => setIsEditingProfile(true)}
                >
                  <Pencil size={16} />
                  <span>Edit Profile</span>
                </button>
              ) : (
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    className={secondaryButtonClass}
                    onClick={handleCancelProfileEdit}
                  >
                    <X size={16} />
                    <span>Cancel</span>
                  </button>

                  <button
                    type="button"
                    className={primaryButtonClass}
                    onClick={handleSaveProfile}
                  >
                    <Save size={16} />
                    <span>Save Changes</span>
                  </button>
                </div>
              )}
            </div>

            {!isEditingProfile ? (
              <div className="space-y-4 border-t border-slate-700 pt-4">
                <div className="flex flex-col">
                  <span className="text-sm opacity-70">Name</span>
                  <span className="text-base font-medium">
                    {user?.name || "Not available"}
                  </span>
                </div>

                <div className="flex flex-col">
                  <span className="text-sm opacity-70">Email</span>
                  <span className="text-base font-medium">
                    {user?.email || "Not available"}
                  </span>
                </div>

                <div className="flex flex-col">
                  <span className="text-sm opacity-70">Organization</span>
                  <span className="text-base font-medium">
                    {user?.organization || "Not available"}
                  </span>
                </div>
              </div>
            ) : (
              <div className="space-y-4 border-t border-slate-700 pt-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="flex flex-col gap-2">
                    <label htmlFor="firstName" className={labelClass}>
                      First Name
                    </label>
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      value={profileData.firstName}
                      onChange={handleProfileChange}
                      placeholder="Enter first name"
                      className={inputClass}
                    />
                  </div>

                  <div className="flex flex-col gap-2">
                    <label htmlFor="lastName" className={labelClass}>
                      Last Name
                    </label>
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      value={profileData.lastName}
                      onChange={handleProfileChange}
                      placeholder="Enter last name"
                      className={inputClass}
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label htmlFor="organization" className={labelClass}>
                    Organization
                  </label>
                  <input
                    id="organization"
                    name="organization"
                    type="text"
                    value={profileData.organization}
                    onChange={handleProfileChange}
                    placeholder="Enter organization name"
                    className={inputClass}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Change Password Card */}
          <div className={cardClass}>
            <h3 className="text-lg font-semibold">Change Password</h3>

            <div className="mt-4 space-y-4">
              <PasswordInput
                id="currentPassword"
                label="Current Password"
                name="currentPassword"
                value={passwordData.currentPassword}
                placeholder="Enter current password"
                showPassword={showCurrentPassword}
                setShowPassword={setShowCurrentPassword}
                onChange={handlePasswordChange}
                inputClass={inputClass}
                labelClass={labelClass}
              />

              <PasswordInput
                id="newPassword"
                label="New Password"
                name="newPassword"
                value={passwordData.newPassword}
                placeholder="Enter new password"
                showPassword={showNewPassword}
                setShowPassword={setShowNewPassword}
                onChange={handlePasswordChange}
                inputClass={inputClass}
                labelClass={labelClass}
              />

              <PasswordInput
                id="confirmPassword"
                label="Confirm Password"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                placeholder="Confirm new password"
                showPassword={showConfirmPassword}
                setShowPassword={setShowConfirmPassword}
                onChange={handlePasswordChange}
                inputClass={inputClass}
                labelClass={labelClass}
              />

              <button type="button" className={primaryButtonClass}>
                Update Password
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

type PasswordInputProps = {
  id: string;
  label: string;
  name: string;
  value: string;
  placeholder: string;
  showPassword: boolean;
  setShowPassword: React.Dispatch<React.SetStateAction<boolean>>;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  inputClass: string;
  labelClass: string;
};

function PasswordInput({
  id,
  label,
  name,
  value,
  placeholder,
  showPassword,
  setShowPassword,
  onChange,
  inputClass,
  labelClass,
}: PasswordInputProps) {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className={labelClass}>
        {label}
      </label>

      <div className="relative flex items-center">
        <input
          id={id}
          name={name}
          type={showPassword ? "text" : "password"}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`${inputClass} pr-10`}
        />

        <button
          type="button"
          onClick={() => setShowPassword((prev) => !prev)}
          aria-label={showPassword ? `Hide ${label}` : `Show ${label}`}
          className="absolute right-3 text-slate-400 transition hover:text-cyan-300"
        >
          {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </div>
    </div>
  );
}

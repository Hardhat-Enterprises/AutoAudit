import React, { useState } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Lock,
  Mail,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useAuth } from "../../../context/AuthContext";

const socialButtons = [
  {
    label: "Google",
    provider: "google",
    icon: (
      <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
        <path
          fill="#FFC107"
          d="M43.611 20.083H42V20H24v8h11.303C33.915 32.659 29.275 36 24 36c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.962 3.038l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.651-.389-3.917z"
        />
        <path
          fill="#FF3D00"
          d="M6.306 14.691l6.571 4.819C14.655 16.108 19.001 12 24 12c3.059 0 5.842 1.154 7.962 3.038l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"
        />
        <path
          fill="#4CAF50"
          d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.254 0-9.881-3.317-11.288-7.946l-6.501 5.007C9.535 39.556 16.227 44 24 44z"
        />
        <path
          fill="#1976D2"
          d="M43.611 20.083H42V20H24v8h11.303c-.681 1.793-1.815 3.356-3.245 4.571l.001-.001 6.19 5.238C36.993 39.129 44 34 44 24c0-1.341-.138-2.651-.389-3.917z"
        />
      </svg>
    ),
  },
];

const SignInPanel = ({ onLogin, onSignUpClick }) => {
  const auth = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: true,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Vite exposes env vars via import.meta.env (and they must be prefixed with VITE_)
  const apiBaseUrl = import.meta.env.VITE_API_URL;

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (onLogin) {
        await onLogin(formData.email, formData.password, formData.remember);
      } else {
        await auth.login(formData.email, formData.password, formData.remember);
      }
    } catch (err) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    if (isLoading) return;
    setError(null);

    if (!apiBaseUrl) {
      setError("Missing API configuration. Please set VITE_API_URL.");
      return;
    }

    if (provider === "google") {
      // Backend-driven OAuth redirect flow.
      // The callback will land on: /auth/google/callback#access_token=...
      window.location.assign(`${apiBaseUrl}/v1/auth/google/authorize`);
      return;
    }

    setError("Unsupported provider.");
  };

  return (
    <section className="login-form-section">
      <div className="login-form-card">
        <div className="login-form-header">
          <h2>Welcome Back</h2>
          <p>Sign in to access your compliance dashboard and security reports.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && (
            <div className="error-message" style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              color: '#ef4444',
              marginBottom: '16px'
            }}>
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@company.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="form-options">
            <label className="checkbox-wrapper">
              <input
                type="checkbox"
                name="remember"
                checked={formData.remember}
                onChange={handleChange}
              />
              <span>Remember me</span>
            </label>
            <a className="forgot-link" href="#">
              Forgot password?
            </a>
          </div>

          <button type="submit" className="btn-signin" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="divider">
          <span>Or sign in with</span>
        </div>

        <div className={`social-login ${socialButtons.length === 1 ? "single" : ""}`}>
          {socialButtons.map((button) => (
            <button
              key={button.label}
              type="button"
              className="social-btn"
              onClick={() => handleSocialLogin(button.provider)}
              disabled={isLoading || button.disabled}
              aria-disabled={isLoading || button.disabled ? "true" : "false"}
              title={button.disabled ? "Coming soon" : `Continue with ${button.label}`}
            >
              <span className={`social-icon social-icon--${button.provider}`} aria-hidden="true">
                {button.icon}
              </span>
              <span className="social-label">{button.label}</span>
            </button>
          ))}
        </div>

        <p className="signup-text">
          Don&apos;t have an account?{" "}
          <button type="button" onClick={onSignUpClick}>
            Create one
          </button>
        </p>
      </div>
    </section>
  );
};

export default SignInPanel;

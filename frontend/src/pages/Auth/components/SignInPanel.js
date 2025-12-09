import React, { useState } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ShieldCheck,
} from "lucide-react";

const SignInPanel = ({ onLogin, onSignUpClick }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: false,
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (onLogin) {
      onLogin(formData);
    }
  };

  return (
    <section className="login-form-section">
      <div className="login-form-card">
        <div className="login-form-header">
          <h2>Welcome Back</h2>
          <p>Sign in to access your compliance dashboard and security reports.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
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
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
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

          <button type="submit" className="btn-signin">
            <span>Sign In</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="divider">
          <span>or continue with</span>
        </div>

        <div className="social-login single">
          <button type="button" className="social-btn">
            <span className="social-icon">G</span>
            Sign in with Google
          </button>
        </div>

        <p className="signup-text">
          Don&apos;t have an account?{" "}
          <button type="button" onClick={onSignUpClick}>
            Create one
          </button>
        </p>

        <div className="security-info">
          <div className="security-icon-box">
            <ShieldCheck size={18} />
          </div>
          <div className="security-info-text">
            <h4>Secure Enterprise Access</h4>
            <p>Your connection is encrypted and monitored for compliance.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SignInPanel;

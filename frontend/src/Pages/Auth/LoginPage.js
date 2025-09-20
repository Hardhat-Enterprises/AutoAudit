import React, { useState } from 'react';
import './LoginPage.css';

export default function LoginPage({ onLogin, onSignUpClick }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = () => {
    onLogin();
  };

  return (
    <div className="login-container">
      <nav className="top-nav">
        <div className="navlinks">
          <a href="/" className="home-link" role="button" aria-label="Go to Home">
            Home
          </a>
        </div>
      </nav>

      <div className="login-right">
        <img src="/bg.jpg" alt="Login bg" className="bg-img" />
        <div className="image-overlay"></div>
      </div>

      <div className="login-left">
        <div className="login-content">
          <div className="logo-section">
            <img src="/logo.png" alt="AutoAudit Logo" className="logo-img" />
            <h1>AutoAudit</h1>
            <p className="subtitle">Microsoft 365 Compliance Platform</p>
          </div>

          <div className="login-form">
            <div className="form-header">
              <h2>Sign In</h2>
              <p>Access your compliance dashboard and security insights</p>
            </div>

            <div className="form-fields">
              <div className="field-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@company.com"
                />
              </div>

              <div className="field-group">
                <label>Password</label>
                <div className="password-field">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="password-toggle"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>

              <div className="form-options">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  Remember me
                </label>
                <a href="#" className="forgot-link">Forgot password?</a>
              </div>

              <button onClick={handleSubmit} className="signin-btn">
                🔐 Sign In
              </button>

              <div className="signup-redirect">
                <span>Don't have an account? </span>
                <button onClick={onSignUpClick} className="signup-link">
                  Sign Up
                </button>
              </div>
            </div>

            <div className="security-notice">
              <div className="security-content">
                <span className="security-icon">🛡️</span>
                <div>
                  <h3>Secure Enterprise Access</h3>
                  <p>Your connection is encrypted and monitored for compliance with enterprise security standards</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from "react";
import "./LoginPage.css";
import "./SignUpPage.css";
import LoginHeader from "./components/LoginHeader";
import LandingFooter from "../Landing/components/LandingFooter";
import SignupBrandPanel from "./components/SignupBrandPanel";
import SignupFormPanel from "./components/SignupFormPanel";

const emptyForm = {
  firstName: "",
  lastName: "",
  email: "",
  organizationName: "",
  password: "",
  confirmPassword: "",
};

export default function SignUpPage({ onSignUp, onBackToLogin }) {

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    organizationName: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState(emptyForm);


  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };


  const handleSubmit = async () => {
    setError('');
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    if (!agreeTerms) {
      alert('Please agree to the terms and conditions');
      return;
    }
    if (!onSignUp) return;

    setIsSubmitting(true);
    try {
      await onSignUp(formData);
    } catch (err) {
      const message = err?.message || 'Sign up failed. Please try again.';
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="signup-container">
       <nav className="top-nav">
        <div className="navlinks">
          <a href="/" className="home-link" role="button" aria-label="Go to Home">
            Home
          </a>
        </div>
      </nav>
      <div className="signup-right">
        <picture>
          <source srcSet="/bg.webp" type="image/webp" />
          <img src="/bg.jpg" alt="Signup bg" className="bg-img" loading="lazy" />
        </picture>
        <div className="image-overlay"></div>
      </div>

      <div className="signup-left">
        <div className="signup-content">
          <div className="logo-section">
            <picture>
              <source srcSet="/AutoAudit.webp" type="image/webp" />
              <img src="/AutoAudit.png" alt="AutoAudit Logo" className="logo-img" loading="lazy" />
            </picture>
            <h1>AutoAudit</h1>
            <p className="subtitle">Microsoft 365 Compliance Platform</p>
          </div>

          <div className="signup-form">
            <div className="form-header">
              <h2>Create Account</h2>
              <p>Start your compliance journey with AutoAudit</p>
            </div>

            <div className="form-fields">
              <div className="name-row">
                <div className="field-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    placeholder="Enter your first name"
                  />
                </div>

                <div className="field-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    placeholder="Enter your last name"
                  />
                </div>
              </div>

              <div className="field-group">
                <label>Email Address</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="your.email@company.com"
                />
              </div>

              <div className="field-group">
                <label>Organization Name</label>
                <input
                  type="text"
                  name="organizationName"
                  value={formData.organizationName}
                  onChange={handleInputChange}
                  placeholder="Enter your organization name"
                />
              </div>

              <div className="field-group">
                <label>Password</label>
                <div className="password-field">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Create a strong password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="password-toggle"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="field-group">
                <label>Confirm Password</label>
                <div className="password-field">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="password-toggle"
                    aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                  >
                    {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="form-options">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={agreeTerms}
                    onChange={(e) => setAgreeTerms(e.target.checked)}
                  />
                I agree to the&nbsp; <a href="#" className="terms-link">Terms & Conditions</a>&nbsp;and&nbsp;<a href="#" className="terms-link">Privacy Policy</a>
                </label>
              </div>

              <button onClick={handleSubmit} className="signup-btn" disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create Account'}
              </button>
              {error && <div className="signup-error">{error}</div>}

              <div className="login-redirect">
                <span>Already have an account? </span>
                <button onClick={onBackToLogin} className="login-link">
                  Sign In
                </button>
              </div>
            </div>

            <div className="security-notice">
              <div className="security-content">
                <span className="security-icon" aria-hidden="true">
                  <ShieldCheck size={18} strokeWidth={2.2} />
                </span>
                <div>
                  <h3>Enterprise Security Standards</h3>
                  <p>Your data is protected with enterprise-grade encryption and follows strict compliance protocols</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

  const handleFormSubmit = (payload) => {
    onSignUp(payload);
    setFormData(emptyForm);
  };

  return (
    <div className="login-page signup-page">
      <LoginHeader />
      <main className="login-main signup-main">
        <SignupBrandPanel />
        <SignupFormPanel
          formData={formData}
          onFormChange={handleFormChange}
          onSubmit={handleFormSubmit}
          onBackToLogin={onBackToLogin}
        />
      </main>
      <LandingFooter />

    </div>
  );
}

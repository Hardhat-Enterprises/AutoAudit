import React, { useState } from "react";
import { ArrowRight, Eye, EyeOff, Mail, Building, User, ShieldCheck } from "lucide-react";

const TERMS_ERROR_MESSAGE = "Please agree to the terms and privacy policy";
const PASSWORD_MISMATCH_MESSAGE = "These passwords do not match";

const inputFields = [
  {
    name: "firstName",
    label: "First Name",
    icon: <User size={16} />,
    type: "text",
    placeholder: "First name",
  },
  {
    name: "lastName",
    label: "Last Name",
    icon: <User size={16} />,
    type: "text",
    placeholder: "Last name",
  },
  {
    name: "email",
    label: "Email Address",
    icon: <Mail size={16} />,
    type: "email",
    placeholder: "your.email@company.com",
  },
  {
    name: "organizationName",
    label: "Organization Name",
    icon: <Building size={16} />,
    type: "text",
    placeholder: "Enter your organization name",
  },
];

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

const SignupFormPanel = ({ formData, onFormChange, onSubmit, onBackToLogin, submitError }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState("");
  // Vite exposes env vars via import.meta.env (and they must be prefixed with VITE_)
  const apiBaseUrl = import.meta.env.VITE_API_URL;

  const handleAgreeTermsChange = (event) => {
    const checked = event.target.checked;
    setAgreeTerms(checked);

    // Clear stale “agree to terms” error as soon as the user fixes it.
    if (checked && error === TERMS_ERROR_MESSAGE) {
      setError("");
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    onFormChange(name, value);
    if (error) setError("");
  };

  const validate = () => {
    if (!agreeTerms) {
      setError(TERMS_ERROR_MESSAGE);
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError(PASSWORD_MISMATCH_MESSAGE);
      return false;
    }
    // Ensure any previous validation error is cleared before a successful submit.
    if (error) setError("");
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validate()) return;
    await onSubmit({ ...formData, agreeTerms: true });
  };

  const handleSocialSignUp = (provider) => {
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
    <section className="login-form-section signup-form-section" aria-labelledby="signup-form-heading">
      <div className="login-form-card signup-form-card">
        <header className="login-form-header">
          <h2 id="signup-form-heading">Create Account</h2>
          <p>Start your compliance journey with AutoAudit.</p>
        </header>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="signup-form-grid">
            {inputFields.slice(0, 2).map((field) => (
              <label key={field.name} className="signup-field">
                <span>{field.label}</span>
                <div className="input-wrapper">
                  <span className="input-icon" aria-hidden="true">
                    {field.icon}
                  </span>
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    required
                  />
                </div>
              </label>
            ))}
          </div>

          {inputFields.slice(2).map((field) => (
            <label key={field.name} className="signup-field">
              <span>{field.label}</span>
              <div className="input-wrapper">
                <span className="input-icon" aria-hidden="true">
                  {field.icon}
                </span>
                <input
                  type={field.type}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                />
              </div>
            </label>
          ))}

          <label className="signup-field">
            <span>Password</span>
            <div className="input-wrapper">
              <span className="input-icon" aria-hidden="true">
                <ShieldCheck size={16} />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </label>

          <label className="signup-field">
            <span>Confirm Password</span>
            <div className="input-wrapper">
              <span className="input-icon" aria-hidden="true">
                <ShieldCheck size={16} />
              </span>
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </label>

          <label className="checkbox-wrapper signup-checkbox">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={handleAgreeTermsChange}
            />
            <span>
              I agree to the <a href="/#terms">Terms & Conditions</a> and <a href="/#privacy">Privacy Policy</a>
            </span>
          </label>

          {(error || submitError) && (
            <p className="signup-error" role="alert">
              {error || submitError}
            </p>
          )}

          <button type="submit" className="btn-signin signup-submit">
            <span>Create Account</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="divider">
          <span>Or sign up with</span>
        </div>

        <div className={`social-login ${socialButtons.length === 1 ? "single" : ""}`}>
          {socialButtons.map((button) => (
            <button
              key={button.label}
              type="button"
              className="social-btn"
              onClick={() => handleSocialSignUp(button.provider)}
              disabled={button.disabled}
              aria-disabled={button.disabled ? "true" : "false"}
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
          Already have an account? <button type="button" onClick={onBackToLogin}>Sign In</button>
        </p>
      </div>
    </section>
  );
};

export default SignupFormPanel;

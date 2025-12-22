import React, { useState } from "react";
import { Eye, EyeOff, Mail, Building, User, ShieldCheck } from "lucide-react";

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
    icon: (
      <svg width="16" height="16" viewBox="0 0 18 18" fill="currentColor" aria-hidden="true">
        <path d="M9 0C4.029 0 0 4.029 0 9c0 4.492 3.291 8.217 7.594 8.892V11.6h-2.286V9h2.286V7.018c0-2.255 1.343-3.501 3.402-3.501.987 0 2.018.176 2.018.176v2.214h-1.137c-1.12 0-1.469.694-1.469 1.406V9h2.498l-.4 2.6h-2.098v6.292C14.709 17.217 18 13.492 18 9c0-4.971-4.029-9-9-9z" />
      </svg>
    ),
  },
  {
    label: "Microsoft",
    icon: (
      <svg width="16" height="16" viewBox="0 0 18 18" fill="currentColor" aria-hidden="true">
        <path d="M9 0C4.029 0 0 4.029 0 9s4.029 9 9 9 9-4.029 9-9-4.029-9-9-9zm3.15 6.75h-1.8c-.248 0-.45.202-.45.45v.9h2.25l-.45 2.25H9.9v5.4H7.2v-5.4H5.85V8.1h1.35v-.9c0-1.243.957-2.25 2.25-2.25h2.25v2.25z" />
      </svg>
    ),
  },
];

const SignupFormPanel = ({ formData, onFormChange, onSubmit, onBackToLogin }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    onFormChange(name, value);
    if (error) setError("");
  };

  const validate = () => {
    if (!agreeTerms) {
      setError("Please agree to the terms and privacy policy");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    return true;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) return;
    onSubmit({ ...formData, agreeTerms: true });
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
              onChange={(event) => setAgreeTerms(event.target.checked)}
            />
            <span>
              I agree to the <a href="/#terms">Terms & Conditions</a> and <a href="/#privacy">Privacy Policy</a>
            </span>
          </label>

          {error && (
            <p className="signup-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" className="btn-signin signup-submit">
            <span role="img" aria-hidden="true">
              🚀
            </span>
            Create Account
          </button>
        </form>

        <div className="divider">
          <span>Or sign up with</span>
        </div>

        <div className="social-login">
          {socialButtons.map((button) => (
            <button key={button.label} type="button" className="social-btn">
              {button.icon}
              {button.label}
            </button>
          ))}
        </div>

        <p className="signup-text">
          Already have an account? <button type="button" onClick={onBackToLogin}>Sign In</button>
        </p>

        <div className="signup-security">
          <span className="signup-security__icon" aria-hidden="true">
            🛡️
          </span>
          <div>
            <h4>Enterprise Security Standards</h4>
            <p>Your data is protected with enterprise-grade encryption and strict compliance controls.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SignupFormPanel;

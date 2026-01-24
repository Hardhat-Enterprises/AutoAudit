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
  const [formData, setFormData] = useState(emptyForm);
  const [submitError, setSubmitError] = useState("");

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    if (submitError) {
      setSubmitError("");
    }
  };

  const getSubmitErrorMessage = (error) => {
    const message = error?.message || "Sign up failed. Please try again.";
    if (message === "REGISTER_USER_ALREADY_EXISTS") {
      return "An account with this email already exists.";
    }
    return message;
  };

  const handleFormSubmit = async (payload) => {
    if (!onSignUp) return;
    setSubmitError("");
    try {
      await onSignUp(payload);
      setFormData(emptyForm);
    } catch (error) {
      setSubmitError(getSubmitErrorMessage(error));
    }
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
          submitError={submitError}
        />
      </main>
      <LandingFooter />
    </div>
  );
}

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

  const handleFormChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };

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

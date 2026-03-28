import React, { useState } from "react";
import "./LoginPage.css";
import "./SignUpPage.css";
import LandingHeader from "../Landing/components/LandingHeader";
import LandingFooter from "../Landing/components/LandingFooter";
import SignupBrandPanel from "./components/SignupBrandPanel";
import SignupFormPanel from "./components/SignupFormPanel";
import type { SignUpFormData, SignUpSubmitPayload } from "./signUpTypes";

export type { SignUpFormData, SignUpSubmitPayload } from "./signUpTypes";

const emptyForm: SignUpFormData = {
  firstName: "",
  lastName: "",
  email: "",
  organizationName: "",
  password: "",
  confirmPassword: "",
};

export type SignUpPageProps = {
  onSignUp: (payload: SignUpSubmitPayload) => Promise<void>;
  onBackToLogin: () => void;
}

export default function SignUpPage({ onSignUp, onBackToLogin }: SignUpPageProps) {
  const [formData, setFormData] = useState<SignUpFormData>(emptyForm);
  const [submitError, setSubmitError] = useState("");

  const handleFormChange = (field: keyof SignUpFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    if (submitError) {
      setSubmitError("");
    }
  };

  const getSubmitErrorMessage = (error: unknown): string => {
    const message =
      error instanceof Error ? error.message : "Sign up failed. Please try again.";
    if (message === "REGISTER_USER_ALREADY_EXISTS") {
      return "An account with this email already exists.";
    }
    return message;
  };

  const handleFormSubmit = async (payload: SignUpSubmitPayload) => {
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
      <LandingHeader />
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

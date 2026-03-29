import React, { useState } from "react";
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
};

export default function SignUpPage({ onSignUp, onBackToLogin }: SignUpPageProps) {
  const [formData, setFormData] = useState<SignUpFormData>(emptyForm);
  const [submitError, setSubmitError] = useState("");

  const handleFormChange = (field: keyof SignUpFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    if (submitError) setSubmitError("");
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
    <div className="min-h-screen flex flex-col bg-[#081b2e]">
      <LandingHeader />

      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="grid w-full max-w-6xl gap-10 lg:grid-cols-2">
          
          {/* Left side (branding) */}
          <div className="hidden lg:flex items-center justify-center">
            <SignupBrandPanel />
          </div>

          {/* Right side (form) */}
          <div className="flex items-center justify-center">
            <SignupFormPanel
              formData={formData}
              onFormChange={handleFormChange}
              onSubmit={handleFormSubmit}
              onBackToLogin={onBackToLogin}
              submitError={submitError}
            />
          </div>

        </div>
      </main>

      <LandingFooter />
    </div>
  );
}
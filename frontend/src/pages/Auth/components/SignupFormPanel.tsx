import React, { useState, type ChangeEvent, type FormEvent, type ReactElement } from "react";
import { ArrowRight, Eye, EyeOff, Mail, Building, User, ShieldCheck } from "lucide-react";
import type { SignUpFormData, SignUpSubmitPayload } from "../signUpTypes";

const TERMS_ERROR_MESSAGE = "Please agree to the terms and privacy policy";
const PASSWORD_MISMATCH_MESSAGE = "These passwords do not match";

type SignupInputFieldName = "firstName" | "lastName" | "email" | "organizationName";

type InputFieldConfig = {
  name: SignupInputFieldName;
  label: string;
  icon: React.ReactNode;
  type: "text" | "email";
  placeholder: string;
};

const inputFields: InputFieldConfig[] = [
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

type SocialButtonConfig = {
  label: string;
  provider: string;
  icon: ReactElement;
  disabled?: boolean;
};

const socialButtons: SocialButtonConfig[] = [
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

export type SignupFormPanelProps = {
  formData: SignUpFormData;
  onFormChange: (field: keyof SignUpFormData, value: string) => void;
  onSubmit: (payload: SignUpSubmitPayload) => void | Promise<void>;
  onBackToLogin: () => void;
  submitError: string;
};

const SignupFormPanel = ({
  formData,
  onFormChange,
  onSubmit,
  onBackToLogin,
  submitError,
}: SignupFormPanelProps) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [error, setError] = useState("");
  const apiBaseUrl = import.meta.env.VITE_API_URL;

  const handleAgreeTermsChange = (event: ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    setAgreeTerms(checked);

    if (checked && error === TERMS_ERROR_MESSAGE) {
      setError("");
    }
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    onFormChange(name as keyof SignUpFormData, value);
    if (error) setError("");
  };

  const validate = (): boolean => {
    if (!agreeTerms) {
      setError(TERMS_ERROR_MESSAGE);
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError(PASSWORD_MISMATCH_MESSAGE);
      return false;
    }
    if (error) setError("");
    return true;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validate()) return;
    await onSubmit({ ...formData, agreeTerms: true });
  };

  const handleSocialSignUp = (provider: string) => {
    if (!apiBaseUrl) {
      setError("Missing API configuration. Please set VITE_API_URL.");
      return;
    }

    if (provider === "google") {
      window.location.assign(`${apiBaseUrl}/v1/auth/google/authorize`);
      return;
    }

    setError("Unsupported provider.");
  };

  return (
    <section
      className="flex w-full items-center justify-center"
      aria-labelledby="signup-form-heading"
    >
      <div className="w-full max-w-lg rounded-3xl bg-[#0d2746] p-8 shadow-2xl">
        <header className="mb-8">
          <h2 id="signup-form-heading" className="text-5xl font-semibold text-white">
            Create Account
          </h2>
          <p className="mt-3 text-lg text-blue-100">
            Start your compliance journey with AutoAudit.
          </p>
        </header>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {inputFields.slice(0, 2).map((field) => (
              <label key={field.name} className="flex flex-col gap-2">
                <span className="text-base font-medium text-white">{field.label}</span>
                <div className="flex items-center rounded-2xl border border-blue-800 bg-[#173454] px-4 py-3 focus-within:border-blue-500">
                  <span className="mr-3 text-blue-200" aria-hidden="true">
                    {field.icon}
                  </span>
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    required
                    className="w-full bg-transparent text-white outline-none placeholder:text-blue-200"
                  />
                </div>
              </label>
            ))}
          </div>

          {inputFields.slice(2).map((field) => (
            <label key={field.name} className="flex flex-col gap-2">
              <span className="text-base font-medium text-white">{field.label}</span>
              <div className="flex items-center rounded-2xl border border-blue-800 bg-[#173454] px-4 py-3 focus-within:border-blue-500">
                <span className="mr-3 text-blue-200" aria-hidden="true">
                  {field.icon}
                </span>
                <input
                  type={field.type}
                  name={field.name}
                  value={formData[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required
                  className="w-full bg-transparent text-white outline-none placeholder:text-blue-200"
                />
              </div>
            </label>
          ))}

          <label className="flex flex-col gap-2">
            <span className="text-base font-medium text-white">Password</span>
            <div className="flex items-center rounded-2xl border border-blue-800 bg-[#173454] px-4 py-3 focus-within:border-blue-500">
              <span className="mr-3 text-blue-200" aria-hidden="true">
                <ShieldCheck size={16} />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                required
                className="w-full bg-transparent text-white outline-none placeholder:text-blue-200"
              />
              <button
                type="button"
                className="ml-3 text-blue-200 hover:text-white"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-base font-medium text-white">Confirm Password</span>
            <div className="flex items-center rounded-2xl border border-blue-800 bg-[#173454] px-4 py-3 focus-within:border-blue-500">
              <span className="mr-3 text-blue-200" aria-hidden="true">
                <ShieldCheck size={16} />
              </span>
              <input
                type={showConfirmPassword ? "text" : "password"}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                required
                className="w-full bg-transparent text-white outline-none placeholder:text-blue-200"
              />
              <button
                type="button"
                className="ml-3 text-blue-200 hover:text-white"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </label>

          <label className="flex items-start gap-3 text-sm text-blue-100">
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={handleAgreeTermsChange}
              className="mt-1"
            />
            <span>
              I agree to the{" "}
              <a href="/#terms" className="text-white underline">
                Terms & Conditions
              </a>{" "}
              and{" "}
              <a href="/#privacy" className="text-white underline">
                Privacy Policy
              </a>
            </span>
          </label>

          {(error || submitError) && (
            <p className="text-sm text-red-400" role="alert">
              {error || submitError}
            </p>
          )}

          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-500 py-4 text-lg font-semibold text-white transition hover:bg-blue-600"
          >
            <span>Create Account</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="relative my-8 text-center">
          <div className="absolute left-0 top-1/2 h-px w-full -translate-y-1/2 bg-blue-800" />
          <span className="relative bg-[#0d2746] px-4 text-sm uppercase tracking-widest text-blue-100">
            Or sign up with
          </span>
        </div>

        <div className="flex justify-center">
          {socialButtons.map((button) => (
            <button
              key={button.label}
              type="button"
              className="flex min-w-[230px] items-center justify-center gap-3 rounded-2xl border border-blue-800 bg-[#173454] px-6 py-3 text-white transition hover:bg-[#1d3d63]"
              onClick={() => handleSocialSignUp(button.provider)}
              disabled={Boolean(button.disabled)}
              aria-disabled={button.disabled ? "true" : "false"}
              title={button.disabled ? "Coming soon" : `Continue with ${button.label}`}
            >
              <span
                className="flex h-9 w-9 items-center justify-center rounded-full bg-[#23476f]"
                aria-hidden="true"
              >
                {button.icon}
              </span>
              <span className="font-medium text-white">{button.label}</span>
            </button>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-blue-100">
          Already have an account?{" "}
          <button
            type="button"
            onClick={onBackToLogin}
            className="font-semibold text-white hover:underline"
          >
            Sign In
          </button>
        </p>
      </div>
    </section>
  );
};

export default SignupFormPanel;
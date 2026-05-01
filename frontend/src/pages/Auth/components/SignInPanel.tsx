import React, { useState, type ReactElement, type ChangeEvent, type FormEvent } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Lock,
  Mail,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useAuth } from "../../../context/AuthContext";

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

export type SignInPanelProps = {
  onLogin?: (email: string, password: string, remember?: boolean) => Promise<void>;
  onSignUpClick?: () => void;
};

const SignInPanel = ({ onLogin, onSignUpClick }: SignInPanelProps) => {
  const auth = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: true,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const apiBaseUrl = import.meta.env.VITE_API_URL;

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    if (error) setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (onLogin) {
        await onLogin(formData.email, formData.password, formData.remember);
      } else {
        await auth.login(formData.email, formData.password, formData.remember);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed. Please check your credentials.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    if (isLoading) return;
    setError(null);

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
    <section className="flex items-stretch justify-center rounded-3xl">
      <div className="h-full w-full max-w-120 rounded-[18px] bg-[rgba(15,35,56,0.9)] p-9 shadow-[0_30px_60px_rgba(5,9,20,0.45)]">
        <div>
          <h2 className="mb-2 text-[2rem] leading-tight text-white">Welcome Back</h2>
          <p className="text-[#b0c4de]">
            Sign in to access your compliance dashboard and security reports.
          </p>
        </div>

        <form className="mt-8 flex flex-col gap-5" onSubmit={handleSubmit}>
          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-lg border border-[rgba(239,68,68,0.3)] bg-[rgba(239,68,68,0.1)] px-3 py-3 text-[#ef4444]">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="email" className="mb-[0.4rem] block font-medium text-[#b0c4de]">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-[#3b82f6]" size={18} />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@company.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="w-full rounded-xl border-2 border-[rgba(59,130,246,0.2)] bg-[rgba(255,255,255,0.05)] px-4 py-4 pl-12 text-[1rem] text-white outline-none transition placeholder:text-[#6c7a8d] focus:border-[#3b82f6] focus:bg-[rgba(255,255,255,0.08)] focus:shadow-[0_0_0_4px_rgba(59,130,246,0.12)] disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="mb-[0.4rem] block font-medium text-[#b0c4de]">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-[#3b82f6]" size={18} />
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="w-full rounded-xl border-2 border-[rgba(59,130,246,0.2)] bg-[rgba(255,255,255,0.05)] px-4 py-4 pl-12 pr-12 text-[1rem] text-white outline-none transition placeholder:text-[#6c7a8d] focus:border-[#3b82f6] focus:bg-[rgba(255,255,255,0.08)] focus:shadow-[0_0_0_4px_rgba(59,130,246,0.12)] disabled:cursor-not-allowed disabled:opacity-60"
              />
              <button
                type="button"
                className="absolute right-4 top-1/2 -translate-y-1/2 border-none bg-transparent text-[#b0c4de] transition hover:text-[#3b82f6] disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-[0.9rem]">
            <label className="flex cursor-pointer items-center gap-2 text-[#b0c4de]">
              <input
                type="checkbox"
                name="remember"
                checked={formData.remember}
                onChange={handleChange}
                className="cursor-pointer h-4.5 w-4.5 accent-[#3b82f6]"
              />
              <span>Remember me</span>
            </label>
            <a className="text-[#3b82f6] no-underline" href="#">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            data-testid="form-sign-in"
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[linear-gradient(135deg,#3b82f6_0%,#2563eb_100%)] px-4 py-4 text-[1rem] font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(59,130,246,0.4)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="my-8 flex items-center text-[0.8rem] uppercase tracking-[1px] text-[#b0c4de] before:h-px before:flex-1 before:bg-[rgba(59,130,246,0.2)] before:content-[''] after:h-px after:flex-1 after:bg-[rgba(59,130,246,0.2)] after:content-['']">
          <span className="px-4">Or sign in with</span>
        </div>

        <div
          className={`mb-6 grid gap-4 ${
            socialButtons.length === 1 ? "grid-cols-1 justify-items-center" : "grid-cols-2"
          }`}
        >
          {socialButtons.map((button) => (
            <button
              key={button.label}
              type="button"
              className="flex w-full max-w-70 items-center justify-center gap-2 rounded-xl border-2 border-[rgba(59,130,246,0.2)] bg-[rgba(255,255,255,0.04)] px-4 py-[0.9rem] font-semibold text-white transition hover:-translate-y-0.5 hover:border-[#3b82f6] focus-visible:outline-none focus-visible:shadow-[0_0_0_4px_rgba(59,130,246,0.18)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              onClick={() => handleSocialLogin(button.provider)}
              disabled={isLoading || Boolean(button.disabled)}
              aria-disabled={isLoading || button.disabled ? "true" : "false"}
              title={button.disabled ? "Coming soon" : `Continue with ${button.label}`}
            >
              <span
                className="grid h-8 w-8 place-items-center rounded-[10px] bg-[rgba(255,255,255,0.08)]"
                aria-hidden="true"
              >
                {button.icon}
              </span>
              <span>{button.label}</span>
            </button>
          ))}
        </div>

        <p className="text-center text-[0.95rem] text-[#b0c4de]">
          Don&apos;t have an account?{" "}
          <button
            type="button"
            onClick={onSignUpClick}
            className="border-none bg-transparent font-semibold text-[#3b82f6]"
          >
            Create one
          </button>
        </p>
      </div>
    </section>
  );
};

export default SignInPanel;
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
    <section className="flex justify-center items-stretch rounded-3xl">
      <div className="p-9 w-full h-full max-w-120 rounded-[18px] bg-[rgb(15_35_56/0.9)] shadow-[0_30px_60px_rgb(5_9_20/0.45)]">
        <div>
          <h2 className="mb-2 leading-tight text-white text-[2rem]">Welcome Back</h2>
          <p className="text-[rgb(var(--landing-text-soft))]">
            Sign in to access your compliance dashboard and security reports.
          </p>
        </div>

        <form className="flex flex-col gap-5 mt-8" onSubmit={handleSubmit}>
          {error && (
            <div className="flex gap-2 items-center py-3 px-3 mb-4 rounded-lg border border-[rgb(var(--accent-bad)/0.3)] bg-[rgb(var(--accent-bad)/0.1)] text-[rgb(var(--accent-bad))]">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block font-medium mb-[0.4rem] text-[rgb(var(--landing-text-soft))]">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-[rgb(var(--brand-blue))]" size={18} />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@company.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="py-4 px-4 pl-12 w-full text-white rounded-xl border-2 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed border-[rgb(var(--brand-blue)/0.2)] bg-[rgb(255_255_255/0.05)] text-[1rem] placeholder:text-[rgb(108_122_141)] focus:border-[rgb(var(--brand-blue))] focus:bg-[rgb(255_255_255/0.08)] focus:shadow-[0_0_0_4px_rgb(var(--brand-blue)/0.12)]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block font-medium mb-[0.4rem] text-[rgb(var(--landing-text-soft))]">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-[rgb(var(--brand-blue))]" size={18} />
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={isLoading}
                className="py-4 px-4 pr-12 pl-12 w-full text-white rounded-xl border-2 transition outline-none disabled:opacity-60 disabled:cursor-not-allowed border-[rgb(var(--brand-blue)/0.2)] bg-[rgb(255_255_255/0.05)] text-[1rem] placeholder:text-[rgb(108_122_141)] focus:border-[rgb(var(--brand-blue))] focus:bg-[rgb(255_255_255/0.08)] focus:shadow-[0_0_0_4px_rgb(var(--brand-blue)/0.12)]"
              />
              <button
                type="button"
                className="absolute right-4 top-1/2 bg-transparent border-none transition -translate-y-1/2 disabled:opacity-60 disabled:cursor-not-allowed text-[rgb(var(--landing-text-soft))] hover:text-[rgb(var(--brand-blue))]"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center text-[0.9rem]">
            <label className="flex gap-2 items-center cursor-pointer text-[rgb(var(--landing-text-soft))]">
              <input
                type="checkbox"
                name="remember"
                checked={formData.remember}
                onChange={handleChange}
                className="cursor-pointer h-4.5 w-4.5 accent-[rgb(var(--brand-blue))]"
              />
              <span>Remember me</span>
            </label>
            <a className="no-underline text-[rgb(var(--brand-blue))]" href="#">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            data-testid="form-sign-in"
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[linear-gradient(135deg,#3b82f6_0%,#2563eb_100%)] px-4 py-4 text-[1rem] font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgb(var(--brand-blue)/0.4)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
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

        <div className="flex items-center my-8 uppercase text-[0.8rem] tracking-[1px] text-[rgb(var(--landing-text-soft))] before:h-px before:flex-1 before:bg-[rgb(var(--brand-blue)/0.2)] before:content-[''] after:h-px after:flex-1 after:bg-[rgb(var(--brand-blue)/0.2)] after:content-['']">
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
              className="flex gap-2 justify-center items-center px-4 w-full font-semibold text-white rounded-xl border-2 transition hover:-translate-y-0.5 focus-visible:outline-none disabled:opacity-60 disabled:cursor-not-allowed max-w-70 border-[rgb(var(--brand-blue)/0.2)] bg-[rgb(255_255_255/0.04)] py-[0.9rem] hover:border-[rgb(var(--brand-blue))] focus-visible:shadow-[0_0_0_4px_rgb(var(--brand-blue)/0.18)] disabled:hover:translate-y-0"
              onClick={() => handleSocialLogin(button.provider)}
              disabled={isLoading || Boolean(button.disabled)}
              aria-disabled={isLoading || button.disabled ? "true" : "false"}
              title={button.disabled ? "Coming soon" : `Continue with ${button.label}`}
            >
              <span
                className="grid place-items-center w-8 h-8 rounded-[10px] bg-[rgb(255_255_255/0.08)]"
                aria-hidden="true"
              >
                {button.icon}
              </span>
              <span>{button.label}</span>
            </button>
          ))}
        </div>

        <p className="text-center text-[0.95rem] text-[rgb(var(--landing-text-soft))]">
          Don&apos;t have an account?{" "}
          <button
            type="button"
            onClick={onSignUpClick}
            className="font-semibold bg-transparent border-none text-[rgb(var(--brand-blue))]"
          >
            Create one
          </button>
        </p>
      </div>
    </section>
  );
};

export default SignInPanel;
import React from "react";
import LandingHeader from "../Landing/components/LandingHeader";
import BrandPanel from "./components/BrandPanel";
import SignInPanel from "./components/SignInPanel";
import LandingFooter from "../Landing/components/LandingFooter";

export type LoginPageProps = {
  onLogin: (email: string, password: string, remember?: boolean) => Promise<void>;
  onSignUpClick: () => void;
};

const LoginPage = ({ onLogin, onSignUpClick }: LoginPageProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#081b2e]">
      <LandingHeader />

      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="grid w-full max-w-6xl gap-10 lg:grid-cols-2">
          
          {/* Left side (branding) */}
          <div className="hidden lg:flex items-center justify-center">
            <BrandPanel />
          </div>

          {/* Right side (login form) */}
          <div className="flex items-center justify-center">
            <SignInPanel onLogin={onLogin} onSignUpClick={onSignUpClick} />
          </div>

        </div>
      </main>

      <LandingFooter />
    </div>
  );
};

export default LoginPage;
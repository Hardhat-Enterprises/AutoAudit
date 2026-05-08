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
    <div className="flex flex-col min-h-screen bg-[rgb(8_27_46)]">
      <LandingHeader />

      <main className="flex flex-1 justify-center items-center py-12 px-6">
        <div className="grid gap-10 w-full max-w-6xl lg:grid-cols-2">

          {/* Left side (branding) */}
          <div className="hidden justify-center items-center lg:flex">
            <BrandPanel />
          </div>

          {/* Right side (login form) */}
          <div className="flex justify-center items-center">
            <SignInPanel onLogin={onLogin} onSignUpClick={onSignUpClick} />
          </div>

        </div>
      </main>

      <LandingFooter />
    </div>
  );
};

export default LoginPage;
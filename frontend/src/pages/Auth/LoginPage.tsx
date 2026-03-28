import React from "react";
import "./LoginPage.css";
import "../Landing/LandingPage.css";
import LandingHeader from "../Landing/components/LandingHeader";
import BrandPanel from "./components/BrandPanel";
import SignInPanel from "./components/SignInPanel";
import LandingFooter from "../Landing/components/LandingFooter";

export type LoginPageProps = {
  onLogin: (email: string, password: string, remember?: boolean) => Promise<void>;
  onSignUpClick: () => void;
}

const LoginPage = ({ onLogin, onSignUpClick }: LoginPageProps) => {
  return (
    <div className="login-page">
      <LandingHeader />
      <main className="login-main">
        <BrandPanel />
        <SignInPanel onLogin={onLogin} onSignUpClick={onSignUpClick} />
      </main>
      <LandingFooter />
    </div>
  );
};

export default LoginPage;

import React from "react";
import "./LoginPage.css";
import "../Landing/LandingPage.css";
import LoginHeader from "./components/LoginHeader";
import BrandPanel from "./components/BrandPanel";
import SignInPanel from "./components/SignInPanel";
import LandingFooter from "../Landing/components/LandingFooter";

const LoginPage = ({ onLogin, onSignUpClick }) => {
  return (
    <div className="login-page">
      <LoginHeader />
      <main className="login-main">
        <BrandPanel />
        <SignInPanel onLogin={onLogin} onSignUpClick={onSignUpClick} />
      </main>
      <LandingFooter />
    </div>
  );
};

export default LoginPage;

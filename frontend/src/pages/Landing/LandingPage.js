import React from "react";
import "./LandingPage.css";
import LandingHeader from "./components/LandingHeader";
import HeroSection from "./components/HeroSection";
import StatsSection from "./components/StatsSection";
import FeaturesSection from "./components/FeaturesSection";
import BenefitsSection from "./components/BenefitsSection";
import CTASection from "./components/CTASection";
import LandingFooter from "./components/LandingFooter";

const LandingPage = ({ onSignInClick }) => {
  return (
    <div className="landing-page">
      <LandingHeader
        onSignInClick={onSignInClick}
      />
      <main>
        <HeroSection onSignInClick={onSignInClick} />
        <StatsSection />
        <FeaturesSection />
        <BenefitsSection />
        <CTASection onSignInClick={onSignInClick} />
      </main>
      <LandingFooter />
    </div>
  );
};

export default LandingPage;

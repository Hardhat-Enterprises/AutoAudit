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
  {/* this page should not do an entire call to a component here, we dont need a sign in button at this page - todo */}
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

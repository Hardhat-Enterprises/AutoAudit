import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import "./LandingPage.css";
import LandingHeader from "./components/LandingHeader";
import HeroSection from "./components/HeroSection";
import StatsSection from "./components/StatsSection";
import FeaturesSection from "./components/FeaturesSection";
import BenefitsSection from "./components/BenefitsSection";
import CTASection from "./components/CTASection";
import LandingFooter from "./components/LandingFooter";

const LandingPage = ({ onSignInClick }) => {
  const location = useLocation();

  // Support "/#features" and "/#benefits" nav links without hard reload.
  useEffect(() => {
    if (!location.hash) return;
    const id = location.hash.replace("#", "");
    if (!id) return;

    let attempts = 0;
    const tryScroll = () => {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
      attempts += 1;
      if (attempts < 20) {
        requestAnimationFrame(tryScroll);
      }
    };
    tryScroll();
  }, [location.hash]);

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

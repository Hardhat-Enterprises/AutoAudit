import React from "react";
import { Lock, Bolt, BarChart3 } from "lucide-react";

const floatingCards = [
  {
    icon: Lock,
    title: "99.9% Uptime",
    subtitle: "Enterprise-grade reliability you can trust",
  },
  {
    icon: Bolt,
    title: "Real-Time Monitoring",
    subtitle: "Instant alerts and comprehensive insights",
  },
  {
    icon: BarChart3,
    title: "Actionable Reports",
    subtitle: "Export audit-ready documentation instantly",
  },
];

const HeroSection = ({ onSignInClick }) => {
  return (
    <section className="landing-hero">
      <div className="hero-content">
        <div className="hero-text">
          <h1>Access your compliance dashboard and security insights.</h1>
          <p>
            Compliance made easy for you. View your dashboards anytime,
            anywhere. Automate security monitoring and stay ahead of threats
            with real-time insights.
          </p>
          <div className="hero-buttons">
            <button type="button" className="btn-primary" onClick={onSignInClick}>
              Get Started
            </button>
            <a className="btn-secondary" href="#features">
              Learn More
            </a>
          </div>
        </div>

        <div className="hero-visual" aria-hidden="true">
          {floatingCards.map(({ icon: Icon, title, subtitle }) => (
            <article key={title} className="floating-card">
              <div className="card-icon">
                <Icon size={18} strokeWidth={2.2} />
              </div>
              <h3>{title}</h3>
              <p>{subtitle}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

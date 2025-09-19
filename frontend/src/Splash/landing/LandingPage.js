import React from "react";
import "./LandingPage.css";
import logo from "./logo.png";

const FeatureCard = ({ icon, title, desc }) => (
  <article className="feature-card" tabIndex="0">
    <div className="feature-icon" aria-hidden="true">{icon}</div>
    <h3 className="feature-title">{title}</h3>
    <p className="feature-desc">{desc}</p>
  </article>
);

const LandingPage = ({ onSignInClick, onAboutClick }) => {
  return (
    <div className="landing-page">
      <div className="wrap">
        <header className="nav">
          <div className="brand">
            <div className="logo">
              <img src={logo} alt="AutoAudit Logo" className="logo-img" />
            </div>
          </div>
          <nav className="navlinks">
            <button className="hide-sm nav-btn" onClick={onAboutClick}>About</button>
          
            <button className="signin" onClick={onSignInClick}>Sign In</button>
          </nav>
        </header>

        <section className="hero">
          <div className="frame">
            <h1>
              Access your compliance <br />
              dashboard and <br />
              security insights.
            </h1>
            <p className="sub">
              Compliance made easy for you. View your dashboards anytime, anywhere.
            </p>
            <div className="cta">
              <button className="btn btn-primary" onClick={onSignInClick}>
                Get Started
              </button>
              <a className="btn btn-outline" href="#learn-more">Learn More</a>
            </div>
          </div>
        </section>

        <section id="learn-more" className="features" aria-labelledby="features-title">
          <h2 id="features-title" className="sr-only">Key Features</h2>

          <div className="feature-grid">
            <FeatureCard
              icon={
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              }
              title="Microsoft 365 Integration"
              desc="Seamlessly connect to your Microsoft 365 tenant using secure Graph API integration. Monitor MFA enforcement, audit logging, and conditional access policies in real-time."
            />

            <FeatureCard
              icon={
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M9 17V7h2l4 10h-2l-1-2.5H9.5L8.5 17H9zm2.5-4h2l-1-2.5L11.5 13z M3 3h18v18H3V3z"/>
                  <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" strokeWidth="2"/>
                  <path d="M8 12h8M8 8h8M8 16h5" stroke="currentColor" strokeWidth="2"/>
                </svg>
              }
              title="CIS Benchmark Compliance"
              desc="Automatically assess your cloud configurations against CIS Microsoft 365 Foundations Benchmark. Get instant visibility into compliance gaps and security posture."
            />

            <FeatureCard
              icon={
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
              }
              title="Automated Scanning"
              desc="Continuous monitoring of security settings, external sharing permissions, and policy configurations. Detect misconfigurations before they become security risks."
            />

            <FeatureCard
              icon={
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
              }
              title="Actionable Reports"
              desc="Generate comprehensive compliance reports with risk assessments and remediation recommendations. Export audit-ready documentation for regulatory requirements."
            />
          </div>
        </section>

        <section className="insights">
          <p className="insights-tagline">
            <h2><b>Actionable insights at a glance </b></h2>
          </p>

          <h2 className="why-title">Why Choose AutoAudit?</h2>

          <div className="why-grid">
            <div className="why-card">
              <div className="why-icon">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                  <path d="M12 2l7 4v6c0 5-3.5 9.5-7 10-3.5-.5-7-5-7-10V6l7-4z" />
                </svg>
              </div>
              <h3>Enterprise-Grade Security</h3>
              <p>Bank-level encrypted data handling</p>
            </div>

            <div className="why-card">
              <div className="why-icon">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                  <path d="M13 2L3 14h7v8l11-12h-7z" />
                </svg>
              </div>
              <h3>Fast & Automated</h3>
              <p>Reports in minutes, not days</p>
            </div>

            <div className="why-card">
              <div className="why-icon">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                  <rect x="4" y="10" width="4" height="10" />
                  <rect x="10" y="6" width="4" height="14" />
                  <rect x="16" y="2" width="4" height="18" />
                </svg>
              </div>
              <h3>Audit-Ready Reports</h3>
              <p>Align with regulatory frameworks</p>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default LandingPage;
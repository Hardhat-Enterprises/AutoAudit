import React from "react";
import "./AboutUs.css";
import "./LandingPage.css";
import { landingFeatures } from "./featuresData";
import LandingFooter from "./components/LandingFooter";
import LandingHeader from "./components/LandingHeader";

const AboutUs = ({ onBack, onSignInClick, onAboutClick, onContactClick }) => {
  return (
    <div className="about-container">
      <LandingHeader
        onSignInClick={onSignInClick}
        onAboutClick={onAboutClick}
        onHomeClick={onBack}
        onContactClick={onContactClick}
        showSignIn={false}
      />

      <div className="about-content">
        <div className="about-hero">
          <img src="/logo.png" alt="AutoAudit Logo" className="about-logo" />
          <h2>About AutoAudit</h2>
          <p className="about-subtitle">
            Revolutionizing Cloud Compliance for Modern Enterprises
          </p>
        </div>

        <section className="about-section" id="mission">
          <h2>Our Mission</h2>
          <p>
            AutoAudit empowers organizations to maintain robust security postures in their Microsoft 365 environments 
            through automated compliance monitoring and assessment. We bridge the gap between complex regulatory 
            requirements and practical implementation, making enterprise-grade security accessible to teams of all sizes.
          </p>
        </section>

        <section className="about-section" id="features">
          <h2>What We Do</h2>
          <div className="features-overview about-feature-grid">
            {landingFeatures.map((feature) => (
              <article key={feature.title} className="feature-item about-feature-item">
                <div className="feature-icon" aria-hidden="true">
                  {feature.icon}
                </div>
                <div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="about-section about-why" id="benefits">
          <h2>Why AutoAudit?</h2>
          <p>
            In today&apos;s rapidly evolving threat landscape, manual compliance checks are no longer sufficient. 
            Cloud misconfigurations remain one of the leading causes of data breaches, with organizations 
            struggling to maintain visibility across their expanding cloud footprint.
          </p>
          <p>
            AutoAudit was born from the recognition that compliance shouldn&apos;t be a burden. Our platform 
            transforms complex regulatory frameworks into automated, actionable insights, enabling your 
            security team to focus on strategic initiatives rather than manual auditing tasks.
          </p>
        </section>

        <section className="about-section" id="standards">
          <h2>Industry Standards We Support</h2>
          <div className="standards-grid">
            <div className="standard-item">
              <h4>CIS Benchmarks</h4>
              <p>Center for Internet Security Microsoft 365 Foundations</p>
            </div>
            <div className="standard-item">
              <h4>NIST Framework</h4>
              <p>National Institute of Standards and Technology guidelines</p>
            </div>
            <div className="standard-item">
              <h4>ISO 27001</h4>
              <p>International standard for information security management</p>
            </div>
            <div className="standard-item">
              <h4>ASD Essential Eight</h4>
              <p>Australian Signals Directorate mitigation strategies</p>
            </div>
          </div>
        </section>

        <section className="about-section about-commitment" id="commitment">
          <h2>Our Commitment</h2>
          <p>
            We&apos;re committed to providing enterprise-grade security tools that are both powerful and accessible. 
            Our team continuously researches emerging threats and evolving compliance requirements to ensure 
            AutoAudit remains at the forefront of cloud security posture management.
          </p>
          <p>
            Privacy and security are fundamental to everything we do. We employ bank-level encryption, 
            follow zero-trust principles, and maintain strict data governance practices to protect your 
            sensitive information.
          </p>
        </section>

        <section className="about-cta">
          <h2>Ready to Transform Your Compliance Strategy?</h2>
          <p>Join organizations worldwide who trust AutoAudit to secure their cloud environments.</p>
          <button onClick={onBack} className="cta-button">
            Get Started Today
          </button>
        </section>
      </div>

      <LandingFooter />
    </div>
  );
};

export default AboutUs;

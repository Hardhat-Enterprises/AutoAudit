import React from 'react';
import './AboutUs.css';
import logo from './logo.png';

const AboutUs = ({ onBack }) => {
  return (
    <div className="about-container">
      <nav className="about-nav">
        <button onClick={onBack} className="back-btn">← Back to Home</button>
      </nav>

      <div className="about-content">
        <div className="about-hero">
          <img src={logo} alt="AutoAudit Logo" className="about-logo" />
          <h1>About AutoAudit</h1>
          <p className="about-subtitle">Revolutionizing Cloud Compliance for Modern Enterprises</p>
        </div>

        <section className="about-section">
          <h2>Our Mission</h2>
          <p>
            AutoAudit empowers organizations to maintain robust security postures in their Microsoft 365 environments 
            through automated compliance monitoring and assessment. We bridge the gap between complex regulatory 
            requirements and practical implementation, making enterprise-grade security accessible to teams of all sizes.
          </p>
        </section>

        <section className="about-section">
          <h2>What We Do</h2>
          <div className="features-overview">
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M12 2l7 4v6c0 5-3.5 9.5-7 10-3.5-.5-7-5-7-10V6l7-4z" />
                </svg>
              </div>
              <h3>Automated Compliance Scanning</h3>
              <p>Continuously monitor your Microsoft 365 environment against CIS benchmarks and industry standards</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <rect x="4" y="10" width="4" height="10" />
                  <rect x="10" y="6" width="4" height="14" />
                  <rect x="16" y="2" width="4" height="18" />
                </svg>
              </div>
              <h3>Risk Assessment & Reporting</h3>
              <p>Generate comprehensive reports with actionable insights and remediation recommendations</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                  <path d="M13 2L3 14h7v8l11-12h-7z" />
                </svg>
              </div>
              <h3>Real-time Monitoring</h3>
              <p>Stay ahead of security misconfigurations with continuous monitoring and instant alerts</p>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2>Why AutoAudit?</h2>
          <p>
            In today's rapidly evolving threat landscape, manual compliance checks are no longer sufficient. 
            Cloud misconfigurations remain one of the leading causes of data breaches, with organizations 
            struggling to maintain visibility across their expanding cloud footprint.
          </p>
          <p>
            AutoAudit was born from the recognition that compliance shouldn't be a burden. Our platform 
            transforms complex regulatory frameworks into automated, actionable insights, enabling your 
            security team to focus on strategic initiatives rather than manual auditing tasks.
          </p>
        </section>

        <section className="about-section">
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

        <section className="about-section">
          <h2>Our Commitment</h2>
          <p>
            We're committed to providing enterprise-grade security tools that are both powerful and accessible. 
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
    </div>
  );
};

export default AboutUs;
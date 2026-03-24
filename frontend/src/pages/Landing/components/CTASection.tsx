import React from "react";
import { Link } from "react-router-dom";

type CTASectionProps = {
  onSignInClick?: () => void;
};

const CTASection = ({ onSignInClick }: CTASectionProps) => {
  return (
    <section className="landing-cta">
      <div className="cta-content">
        <h2>Ready to transform your compliance process?</h2>
        <p>
          Join thousands of organizations that trust AutoAudit to keep their
          Microsoft 365 environment secure and compliant.
        </p>
        <div className="cta-buttons">
          <button type="button" className="btn-primary" onClick={onSignInClick}>
            Start Free Trial
          </button>
          <Link className="btn-secondary" to="/contact">
            Schedule Demo
          </Link>
        </div>
      </div>
    </section>
  );
};

export default CTASection;

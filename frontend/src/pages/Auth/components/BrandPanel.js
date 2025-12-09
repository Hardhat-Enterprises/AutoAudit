import React from "react";

const brandFeatures = [
  { icon: "🔒", text: "Enterprise-grade security & encryption" },
  { icon: "⚡", text: "Real-time compliance monitoring" },
  { icon: "📊", text: "Actionable reporting & insights" },
];

const BrandPanel = () => {
  return (
    <section className="login-brand" aria-labelledby="brand-title">
      {Array.from({ length: 6 }).map((_, index) => (
        <span
          key={index}
          className={`brand-particle brand-particle-${index + 1}`}
        />
      ))}

      <div className="brand-content">
        <img src="/logo.png" alt="AutoAudit" className="brand-logo" />

        <div className="brand-text" id="brand-title">
          <h1>Access security insights anywhere</h1>
          <p>
            Connect to your Microsoft 365 compliance dashboard, monitor security posture, and act on
            real-time recommendations.
          </p>
        </div>

        <div className="brand-features" aria-label="Platform highlights">
          {brandFeatures.map((feature) => (
            <div key={feature.text} className="brand-feature">
              <span className="brand-feature-icon">{feature.icon}</span>
              <span>{feature.text}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BrandPanel;

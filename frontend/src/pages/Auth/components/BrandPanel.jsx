import React from "react";
import { Lock, Zap, BarChart3 } from "lucide-react";

const brandFeatures = [
  { icon: Lock, text: "Enterprise-grade security & encryption" },
  { icon: Zap, text: "Real-time compliance monitoring" },
  { icon: BarChart3, text: "Actionable reporting & insights" },
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
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img src="/AutoAudit.png" alt="AutoAudit" className="brand-logo" loading="lazy" />
        </picture>

        <div className="brand-text" id="brand-title">
          <h1>Access security insights anywhere</h1>
          <p>
            Connect to your Microsoft 365 compliance dashboard, monitor security posture, and act on
            real-time recommendations.
          </p>
        </div>

        <div className="brand-features" aria-label="Platform highlights">
          {brandFeatures.map((feature) => {
            const Icon = feature.icon;
            return (
              <div key={feature.text} className="brand-feature">
                <span className="brand-feature-icon" aria-hidden="true">
                  <Icon size={18} strokeWidth={2.2} />
                </span>
                <span>{feature.text}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default BrandPanel;

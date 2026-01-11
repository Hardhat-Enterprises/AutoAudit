import React from "react";
import { BarChart3, Lock, Zap } from "lucide-react";

const featureItems = [
  { icon: Zap, text: "Setup in minutes, not hours" },
  { icon: Lock, text: "Bank-level security & encryption" },
  { icon: BarChart3, text: "Real-time compliance monitoring" },
];

const SignupBrandPanel = () => {
  return (
    <section className="login-brand signup-brand" aria-labelledby="signup-brand-title">
      {Array.from({ length: 6 }).map((_, index) => (
        <span key={index} className={`brand-particle brand-particle-${index + 1}`} />
      ))}

      <div className="brand-content signup-brand__content">
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img
            src="/AutoAudit.png"
            alt="AutoAudit"
            className="brand-logo signup-brand__logo"
            loading="lazy"
          />
        </picture>

        <div className="brand-text signup-brand__text" id="signup-brand-title">
          <h1>Start Your Compliance Journey</h1>
          <p>
            Join organizations that rely on AutoAudit to monitor, analyze, and improve their
            Microsoft 365 security posture.
          </p>
        </div>

        <div className="signup-brand__features" aria-label="AutoAudit highlights">
          {featureItems.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.text} className="signup-brand__feature">
                <span className="signup-brand__feature-icon" aria-hidden="true">
                  <Icon size={18} strokeWidth={2.2} />
                </span>
                <span>{item.text}</span>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default SignupBrandPanel;

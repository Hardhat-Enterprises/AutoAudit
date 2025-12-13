import React from "react";
import { Timer, Target, ShieldCheck, Lightbulb } from "lucide-react";

const benefits = [
  {
    icon: Timer,
    title: "Save Time & Resources",
    description:
      "Reduce manual compliance work by 80% so your team can focus on strategic initiatives.",
  },
  {
    icon: Target,
    title: "Stay Ahead of Threats",
    description:
      "Proactive monitoring identifies vulnerabilities before they are exploited.",
  },
  {
    icon: ShieldCheck,
    title: "Ensure Compliance",
    description:
      "Stay aligned with CIS, NIST, ISO 27001, SOC 2, and other regulatory frameworks.",
  },
  {
    icon: Lightbulb,
    title: "Expert Guidance",
    description:
      "Every finding includes prioritized remediation steps to improve security posture.",
  },
];

const BenefitsSection = () => {
  return (
    <section className="landing-benefits" id="benefits">
      <div className="benefits-container">
        <div className="benefits-visual" aria-hidden="true">
          <div className="benefits-graphic" />
          <div className="benefits-network">
            <span className="node node-1" />
            <span className="node node-2" />
            <span className="node node-3" />
            <span className="node node-4" />
            <span className="link link-1" />
            <span className="link link-2" />
            <span className="link link-3" />
          </div>
        </div>

        <div className="benefits-content">
          <h2>Why Choose AutoAudit?</h2>
          {benefits.map((benefit) => (
            <article key={benefit.title} className="benefit-item">
              <div className="benefit-icon">
                <benefit.icon size={18} strokeWidth={2.2} />
              </div>
              <div className="benefit-text">
                <h3>{benefit.title}</h3>
                <p>{benefit.description}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;

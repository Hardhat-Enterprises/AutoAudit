import React from "react";

const features = [
  {
    icon: "🔗",
    title: "Microsoft 365 Integration",
    description:
      "Secure Graph API integration monitors MFA enforcement, audit logging, and conditional access policies in real-time.",
  },
  {
    icon: "📋",
    title: "CIS Benchmark Compliance",
    description:
      "Automatically assess your cloud configurations against CIS Microsoft 365 benchmarks and surface posture gaps.",
  },
  {
    icon: "⚡",
    title: "Automated Scanning",
    description:
      "Continuous monitoring of security settings, sharing permissions, and policies catches issues before they escalate.",
  },
  {
    icon: "📊",
    title: "Actionable Reports",
    description:
      "Generate audit-ready compliance reports with risk assessments and remediation guidance in minutes.",
  },
  {
    icon: "🛡️",
    title: "Enterprise-Grade Security",
    description:
      "Bank-level encrypted data handling with a zero-knowledge architecture keeps your sensitive data in your control.",
  },
  {
    icon: "🚀",
    title: "Fast & Automated",
    description:
      "Automated workflows reduce manual checks and cut audit preparation time by 80%.",
  },
];

const FeatureCard = ({ icon, title, description }) => (
  <article className="feature-card">
    <div className="feature-icon">{icon}</div>
    <h3>{title}</h3>
    <p>{description}</p>
  </article>
);

const FeaturesSection = () => {
  return (
    <section className="landing-features" id="features">
      <div className="section-header">
        <h2 className="section-tag as-heading">Features</h2>
        <h3>Everything you need for compliance</h3>
        <p className="section-subtitle">
          Comprehensive tools and insights to keep your organization secure and
          audit-ready.
        </p>
      </div>

      <div className="features-grid">
        {features.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;

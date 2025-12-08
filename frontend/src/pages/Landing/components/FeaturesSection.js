import React from "react";
import { landingFeatures } from "../featuresData";

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
        {landingFeatures.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;

import React from "react";
import type { LucideIcon } from "lucide-react";
import {
  Link2,
  ClipboardList,
  Bolt,
  BarChart3,
  Shield,
  Rocket,
} from "lucide-react";
import "./AboutUs.css";
import "./LandingPage.css";
import LandingHeader from "./components/LandingHeader";
import LandingFooter from "./components/LandingFooter";

type AboutFeature = {
  icon: LucideIcon;
  title: string;
  description: string;
};

type SupportedStandard = {
  title: string;
  description: string;
};

type AboutUsProps = {
  onSignInClick?: () => void;
};

const features: AboutFeature[] = [
  {
    icon: Link2,
    title: "Microsoft 365 Integration",
    description:
      "Secure Graph API integration monitors MFA enforcement, audit logging, and conditional access policies in real-time.",
  },
  {
    icon: ClipboardList,
    title: "CIS Benchmark Compliance",
    description:
      "Automatically assess cloud configurations against CIS Microsoft 365 Foundations Benchmark and surface posture gaps.",
  },
  {
    icon: Bolt,
    title: "Automated Scanning",
    description:
      "Continuous monitoring of security settings, sharing permissions, and policies catches issues before they escalate.",
  },
  {
    icon: BarChart3,
    title: "Actionable Reports",
    description:
      "Generate audit-ready compliance reports with risk assessments and remediation guidance in minutes.",
  },
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description:
      "Bank-level encrypted data handling with a zero-knowledge architecture keeps your sensitive data in your control.",
  },
  {
    icon: Rocket,
    title: "Fast & Automated",
    description:
      "Automated workflows reduce manual checks and cut audit preparation time by 80%.",
  },
];

const standards: SupportedStandard[] = [
  {
    title: "CIS Benchmarks",
    description: "Center for Internet Security Microsoft 365 Foundations",
  },
  {
    title: "NIST Framework",
    description: "National Institute of Standards and Technology guidelines",
  },
  {
    title: "ISO 27001",
    description: "International standard for information security management",
  },
  {
    title: "ASD Essential Eight",
    description: "Australian Signals Directorate mitigation strategies",
  },
];

const AboutUs = ({ onSignInClick = () => {} }: AboutUsProps) => {
  return (
    <div className="about-page">
      <LandingHeader onSignInClick={onSignInClick} />

      <main>
        <section className="about-hero" id="home">
          <picture>
            <source srcSet="/AutoAudit.webp" type="image/webp" />
            <img src="/AutoAudit.png" alt="AutoAudit" className="hero-logo" />
          </picture>
          <h1>About AutoAudit</h1>
          <p>Revolutionizing Cloud Compliance for Modern Enterprises</p>
        </section>

        <section className="section">
          <h2 className="section-title">Our Mission</h2>
          <div className="section-content">
            <p>
              AutoAudit empowers organizations to maintain robust security postures in their Microsoft 365
              environments through automated compliance monitoring and assessment. We bridge the gap between complex
              regulatory requirements and practical implementation, making enterprise-grade security accessible to
              teams of all sizes.
            </p>
          </div>
        </section>

        <section className="section" id="features">
          <h2 className="section-title">What We Do</h2>
          <div className="features-grid">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <article key={feature.title} className="feature-card">
                  <div className="feature-icon">
                    <Icon size={28} strokeWidth={2.1} />
                  </div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section className="section" id="benefits">
          <h2 className="section-title">Why AutoAudit?</h2>
          <div className="section-content">
            <p>
              In today&apos;s rapidly evolving threat landscape, manual compliance reviews become inefficient. Cloud
              misconfiguration remains one of the leading causes of data breaches, with organizations struggling to
              maintain visibility across their expanding cloud footprints.
            </p>
            <br />
            <p>
              AutoAudit was born from the recognition that compliance shouldn&apos;t be a burden. Our platform
              transforms complex regulatory frameworks into automated, actionable insights, enabling your security team
              to focus on strategic priorities rather than manual auditing tasks.
            </p>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Industry Standards We Support</h2>
          <div className="standards-grid">
            {standards.map((standard) => (
              <article key={standard.title} className="standard-card">
                <h3>{standard.title}</h3>
                <p>{standard.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">Our Commitment</h2>
          <div className="section-content">
            <p>
              We&apos;re committed to providing enterprise-grade security tools that are both powerful and accessible.
              Our team continuously researches emerging threats and evolving compliance requirements to ensure AutoAudit
              remains at the forefront of cloud security posture management.
            </p>
            <br />
            <p>
              Privacy and security are fundamental to everything we do. We employ bank-level encryption, follow
              zero-trust principles, and maintain strict data governance practices to protect your sensitive
              information.
            </p>
          </div>
        </section>

        <section className="cta-section">
          <h2>Ready to Transform Your Compliance Strategy?</h2>
          <p>Join organizations worldwide who trust AutoAudit to secure their cloud environments.</p>
          <button className="cta-button" onClick={onSignInClick}>
            Get Started Today
          </button>
        </section>
      </main>

      <LandingFooter />
    </div>
  );
};

export default AboutUs;

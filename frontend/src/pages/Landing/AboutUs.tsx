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
    <div className="min-h-screen bg-[rgb(var(--landing-bg-base))] font-['Inter',-apple-system,BlinkMacSystemFont,'Segoe_UI',sans-serif] text-white">
      <LandingHeader onSignInClick={onSignInClick} />

      <main className="flex flex-col gap-12">
        <section
          id="home"
          className="relative overflow-hidden bg-linear-to-br from-[rgb(var(--landing-bg-base))] via-[rgb(var(--landing-bg-alt-mid))] to-[rgb(var(--landing-bg-alt-end))] px-[5%] pb-16 pt-24 text-center md:pb-12"
        >
          <div className="pointer-events-none absolute -right-36 -top-44 h-130 w-130 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.1)_0%,transparent_70%)]" />

          <picture>
            <source srcSet="/AutoAudit.webp" type="image/webp" />
            <img
              src="/AutoAudit.png"
              alt="AutoAudit"
              className="block mx-auto mb-8 w-55 drop-shadow-[0_10px_25px_rgb(var(--brand-blue)/0.35)]"
            />
          </picture>

          <h1 className="mb-4 font-bold text-transparent bg-clip-text from-white bg-linear-to-br to-[rgb(var(--brand-blue))] text-[clamp(2.5rem,6vw,3.4rem)]">
            About AutoAudit
          </h1>
          <p className="mx-auto max-w-190 text-[1.2rem] text-[rgb(var(--landing-text-soft))]">
            Revolutionizing Cloud Compliance for Modern Enterprises
          </p>
        </section>

        <section className="px-[5%] md:px-6">
          <h2 className="mb-8 font-semibold text-center text-[clamp(2rem,5vw,2.6rem)] text-[rgb(var(--brand-blue))]">
            Our Mission
          </h2>
          <div className="p-12 mx-auto border md:p-8 max-w-300 rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] backdrop-blur-[10px]">
            <p className="text-[1.05rem] leading-[1.8] text-[rgb(var(--landing-text-soft))]">
              AutoAudit empowers organizations to maintain robust security
              postures in their Microsoft 365 environments through automated
              compliance monitoring and assessment. We bridge the gap between
              complex regulatory requirements and practical implementation,
              making enterprise-grade security accessible to teams of all sizes.
            </p>
          </div>
        </section>

        <section id="features" className="px-[5%] md:px-6">
          <h2 className="mb-8 font-semibold text-center text-[clamp(2rem,5vw,2.6rem)] text-[rgb(var(--brand-blue))]">
            What We Do
          </h2>
          <div className="grid gap-8 mx-auto max-w-300 grid-cols-[repeat(auto-fit,minmax(280px,1fr))]">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <article
                  key={feature.title}
                  className="overflow-hidden relative p-8 border transition-all duration-300 hover:-translate-y-2.5 group rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] hover:border-[rgb(var(--brand-blue))] hover:shadow-[0_20px_40px_rgb(var(--brand-blue)/0.2)]"
                >
                  <div className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-linear-to-br from-[rgb(var(--brand-blue)/0.08)] to-[rgb(var(--brand-blue-deep)/0.08)]" />

                  <div className="flex relative justify-center items-center mb-5 text-white z-1 h-15 w-15 rounded-[15px] bg-linear-to-br from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))]">
                    <Icon size={28} strokeWidth={2.1} />
                  </div>

                  <h3 className="relative mb-3 text-xl font-semibold z-1">
                    {feature.title}
                  </h3>
                  <p className="relative z-1 leading-[1.6] text-[rgb(var(--landing-text-soft))]">
                    {feature.description}
                  </p>
                </article>
              );
            })}
          </div>
        </section>

        <section id="benefits" className="px-[5%] md:px-6">
          <h2 className="mb-8 font-semibold text-center text-[clamp(2rem,5vw,2.6rem)] text-[rgb(var(--brand-blue))]">
            Why AutoAudit?
          </h2>
          <div className="p-12 mx-auto border md:p-8 max-w-300 rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] backdrop-blur-[10px]">
            <p className="text-[1.05rem] leading-[1.8] text-[rgb(var(--landing-text-soft))]">
              In today&apos;s rapidly evolving threat landscape, manual
              compliance reviews become inefficient. Cloud misconfiguration
              remains one of the leading causes of data breaches, with
              organizations struggling to maintain visibility across their
              expanding cloud footprints.
            </p>
            <br />
            <p className="text-[1.05rem] leading-[1.8] text-[rgb(var(--landing-text-soft))]">
              AutoAudit was born from the recognition that compliance
              shouldn&apos;t be a burden. Our platform transforms complex
              regulatory frameworks into automated, actionable insights,
              enabling your security team to focus on strategic priorities
              rather than manual auditing tasks.
            </p>
          </div>
        </section>

        <section className="px-[5%] md:px-6">
          <h2 className="mb-8 font-semibold text-center text-[clamp(2rem,5vw,2.6rem)] text-[rgb(var(--brand-blue))]">
            Industry Standards We Support
          </h2>
          <div className="grid gap-8 mx-auto max-w-300 grid-cols-[repeat(auto-fit,minmax(240px,1fr))]">
            {standards.map((standard) => (
              <article
                key={standard.title}
                className="p-8 rounded-2xl border transition-all duration-300 hover:-translate-y-1.5 border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] hover:border-[rgb(var(--brand-blue))]"
              >
                <h3 className="mb-2.5 font-semibold text-[1.2rem] text-[rgb(var(--brand-blue))]">
                  {standard.title}
                </h3>
                <p className="text-[0.95rem] leading-[1.6] text-[rgb(var(--landing-text-soft))]">
                  {standard.description}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="px-[5%] md:px-6">
          <h2 className="mb-8 font-semibold text-center text-[clamp(2rem,5vw,2.6rem)] text-[rgb(var(--brand-blue))]">
            Our Commitment
          </h2>
          <div className="p-12 mx-auto border md:p-8 max-w-300 rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] backdrop-blur-[10px]">
            <p className="text-[1.05rem] leading-[1.8] text-[rgb(var(--landing-text-soft))]">
              We&apos;re committed to providing enterprise-grade security tools
              that are both powerful and accessible. Our team continuously
              researches emerging threats and evolving compliance requirements
              to ensure AutoAudit remains at the forefront of cloud security
              posture management.
            </p>
            <br />
            <p className="text-[1.05rem] leading-[1.8] text-[rgb(var(--landing-text-soft))]">
              Privacy and security are fundamental to everything we do. We
              employ bank-level encryption, follow zero-trust principles, and
              maintain strict data governance practices to protect your
              sensitive information.
            </p>
          </div>
        </section>

        <section className="mx-[5%] mb-16 rounded-[30px] border border-[rgb(var(--brand-blue)/0.2)] bg-linear-to-br from-[rgb(var(--landing-bg-alt-start))] to-[rgb(var(--landing-bg-base))] px-[5%] py-16 text-center md:mx-6 md:px-6 md:py-12">
          <h2 className="mb-4 font-semibold text-[clamp(2rem,5vw,2.6rem)]">
            Ready to Transform Your Compliance Strategy?
          </h2>
          <p className="mb-8 text-[1.1rem] text-[rgb(var(--landing-text-soft))]">
            Join organizations worldwide who trust AutoAudit to secure their
            cloud environments.
          </p>
          <button
            className="py-3.5 px-10 text-base font-semibold text-white rounded-full transition duration-200 hover:-translate-y-0.5 bg-linear-to-br from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))] hover:shadow-[0_10px_25px_rgb(var(--brand-blue)/0.35)]"
            onClick={onSignInClick}
          >
            Get Started Today
          </button>
        </section>
      </main>

      <LandingFooter />
    </div>
  );
};

export default AboutUs;

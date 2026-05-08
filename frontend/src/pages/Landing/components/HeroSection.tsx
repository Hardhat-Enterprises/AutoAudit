import React from "react";
import type { LucideIcon } from "lucide-react";
import { Lock, Bolt, BarChart3 } from "lucide-react";

type FloatingCard = {
  icon: LucideIcon;
  title: string;
  subtitle: string;
};

const floatingCards: FloatingCard[] = [
  {
    icon: Lock,
    title: "99.9% Uptime",
    subtitle: "Enterprise-grade reliability you can trust",
  },
  {
    icon: Bolt,
    title: "Real-Time Monitoring",
    subtitle: "Instant alerts and comprehensive insights",
  },
  {
    icon: BarChart3,
    title: "Actionable Reports",
    subtitle: "Export audit-ready documentation instantly",
  },
];

type HeroSectionProps = {
  onSignInClick?: () => void;
};

const HeroSection = ({ onSignInClick }: HeroSectionProps) => {
  return (
    <section className="relative isolate overflow-hidden bg-linear-to-br from-[rgb(var(--landing-bg-base))] via-[rgb(var(--landing-bg-mid))] to-[rgb(var(--landing-bg-end))] px-[5%] pt-8 pb-16">
      <div className="pointer-events-none absolute -top-50 -right-50 h-150 w-150 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.15)_0%,transparent_70%)]" />
      <div className="pointer-events-none absolute -bottom-37.5 -left-25 h-105 w-105 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.2)_0%,transparent_70%)]" />

      <div className="grid gap-14 items-center mx-auto max-w-300 grid-cols-[repeat(auto-fit,minmax(280px,1fr))]">
        <div>
          <p className="mb-3 text-sm font-semibold tracking-wide text-white">
            AutoAudit Platform
          </p>
          <h1 className="mb-6 font-bold leading-tight text-transparent bg-clip-text from-white bg-linear-to-br to-[rgb(var(--brand-blue))] text-[clamp(2.5rem,5vw,3.5rem)]">
            Access your compliance dashboard and security insights.
          </h1>
          <p className="leading-relaxed max-w-170 text-[1.2rem] text-[rgb(var(--landing-text-soft))]">
            Compliance made easy for you. View your dashboards anytime,
            anywhere. Automate security monitoring and stay ahead of threats
            with real-time insights.
          </p>
          <div className="flex flex-wrap gap-4 mt-8">
            <button
              type="button"
              className="inline-flex justify-center items-center py-3 px-7 font-semibold text-white rounded-full transition duration-200 hover:-translate-y-0.5 bg-linear-to-br from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))] shadow-[0_8px_30px_rgb(var(--brand-blue)/0.35)] hover:shadow-[0_12px_30px_rgb(var(--brand-blue)/0.5)]"
              onClick={onSignInClick}
            >
              Get Started
            </button>
            <a
              className="inline-flex justify-center items-center py-3 px-7 font-semibold rounded-full border-2 transition duration-200 hover:-translate-y-0.5 border-[rgb(var(--brand-blue))] text-[rgb(var(--brand-blue))] hover:bg-[rgb(var(--brand-blue))] hover:text-[rgb(var(--landing-bg-base))]"
              href="#features"
            >
              Learn More
            </a>
          </div>
        </div>

        <div className="flex flex-col gap-5" aria-hidden="true">
          {floatingCards.map(({ icon: Icon, title, subtitle }) => (
            <article
              key={title}
              className="overflow-hidden relative p-8 border transition duration-300 hover:-translate-y-2 group rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] backdrop-blur-[10px] hover:border-[rgb(var(--brand-blue))] hover:shadow-[0_20px_45px_rgb(var(--brand-blue)/0.2)]"
            >
              <div className="absolute inset-0 opacity-0 transition-opacity duration-300 pointer-events-none group-hover:opacity-100 bg-linear-to-br from-[rgb(var(--brand-blue)/0.15)] to-[rgb(var(--brand-blue)/0.12)]" />
              <div className="inline-flex relative justify-center items-center mb-4 w-12 h-12 border z-1 rounded-[14px] border-[rgb(255_255_255/0.08)] bg-linear-to-br from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))] text-[rgb(236_240_255/0.98)] shadow-[0_10px_22px_rgb(var(--brand-blue)/0.22)]">
                <Icon size={18} strokeWidth={2.2} />
              </div>
              <h3 className="relative mb-2 text-xl font-semibold z-1">{title}</h3>
              <p className="relative leading-relaxed z-1 text-[rgb(var(--landing-text-soft))]">{subtitle}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

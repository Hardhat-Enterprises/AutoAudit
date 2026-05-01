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
    <section className="relative isolate overflow-hidden bg-linear-to-br from-[#0a1628] via-[#0f1f38] to-[#162a4a] px-[5%] pt-8 pb-16">
      <div className="pointer-events-none absolute -top-50 -right-50 h-150 w-150 rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.15)_0%,transparent_70%)]" />
      <div className="pointer-events-none absolute -bottom-37.5 -left-25 h-105 w-105 rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.2)_0%,transparent_70%)]" />

      <div className="mx-auto grid max-w-300 grid-cols-[repeat(auto-fit,minmax(280px,1fr))] items-center gap-14">
        <div>
          <p className="mb-3 text-sm font-semibold tracking-wide text-white">
            AutoAudit Platform
          </p>
          <h1 className="mb-6 bg-linear-to-br from-white to-[#3b82f6] bg-clip-text text-[clamp(2.5rem,5vw,3.5rem)] leading-tight font-bold text-transparent">
            Access your compliance dashboard and security insights.
          </h1>
          <p className="max-w-170 text-[1.2rem] leading-relaxed text-[#b0c4de]">
            Compliance made easy for you. View your dashboards anytime,
            anywhere. Automate security monitoring and stay ahead of threats
            with real-time insights.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-full bg-linear-to-br from-[#3b82f6] to-[#2563eb] px-7 py-3 font-semibold text-white shadow-[0_8px_30px_rgba(59,130,246,0.35)] transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_30px_rgba(59,130,246,0.5)]"
              onClick={onSignInClick}
            >
              Get Started
            </button>
            <a
              className="inline-flex items-center justify-center rounded-full border-2 border-[#3b82f6] px-7 py-3 font-semibold text-[#3b82f6] transition duration-200 hover:-translate-y-0.5 hover:bg-[#3b82f6] hover:text-[#0a1628]"
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
              className="group relative overflow-hidden rounded-[20px] border border-[rgba(59,130,246,0.1)] bg-[rgba(255,255,255,0.03)] p-8 backdrop-blur-[10px] transition duration-300 hover:-translate-y-2 hover:border-[#3b82f6] hover:shadow-[0_20px_45px_rgba(59,130,246,0.2)]"
            >
              <div className="pointer-events-none absolute inset-0 bg-linear-to-br from-[rgba(59,130,246,0.15)] to-[rgba(59,130,246,0.12)] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
              <div className="relative z-1 mb-4 inline-flex h-12 w-12 items-center justify-center rounded-[14px] border border-[rgba(255,255,255,0.08)] bg-linear-to-br from-[#3b82f6] to-[#2563eb] text-[rgba(236,240,255,0.98)] shadow-[0_10px_22px_rgba(59,130,246,0.22)]">
                <Icon size={18} strokeWidth={2.2} />
              </div>
              <h3 className="relative z-1 mb-2 text-xl font-semibold">{title}</h3>
              <p className="relative z-1 leading-relaxed text-[#b0c4de]">{subtitle}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

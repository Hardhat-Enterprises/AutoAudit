import React from "react";
import type { LucideIcon } from "lucide-react";
import { Timer, Target, ShieldCheck, Lightbulb } from "lucide-react";

type Benefit = {
  icon: LucideIcon;
  title: string;
  description: string;
};

const benefits: Benefit[] = [
  {
    icon: Timer,
    title: "Save Time & Resources",
    description:
      "Reduce manual compliance work so your team can focus on strategic initiatives.",
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
      "Stay aligned with cybersecurity frameworks as they get updated with ease",
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
    <section
      className="relative scroll-mt-28 overflow-hidden bg-gradient-to-br from-[rgb(var(--landing-bg-base))] via-[rgb(var(--landing-bg-mid))] to-[rgb(var(--landing-bg-end))] px-[5%] py-24"
      id="benefits"
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgb(var(--brand-blue)/0.08),transparent_62%),radial-gradient(circle_at_88%_22%,rgb(var(--brand-blue-deep)/0.06),transparent_60%)]" />
      <div className="grid relative gap-12 items-center mx-auto max-w-[1200px] grid-cols-[repeat(auto-fit,minmax(280px,1fr))]">
        <div
          className="relative min-h-[320px] overflow-hidden rounded-[24px] border border-[rgb(var(--brand-blue)/0.1)] bg-[radial-gradient(circle_at_20%_20%,rgb(var(--brand-blue)/0.25),transparent_55%),radial-gradient(circle_at_80%_30%,rgb(var(--brand-blue)/0.25),transparent_60%),linear-gradient(135deg,#1e3a5f,#0a1628)]"
          aria-hidden="true"
        >
          <div className="absolute inset-0 opacity-60 bg-[linear-gradient(rgb(255_255_255/0.05)_1px,transparent_1px),linear-gradient(90deg,rgb(255_255_255/0.05)_1px,transparent_1px)] bg-[length:40px_40px]" />
          <div className="absolute inset-0 pointer-events-none">
            <span className="absolute left-[22%] top-[20%] h-4 w-4 rounded-full bg-[rgb(var(--brand-blue))] shadow-[0_0_20px_rgb(var(--brand-blue)/0.8)]" />
            <span className="absolute left-[60%] top-[40%] h-4 w-4 rounded-full bg-[rgb(var(--brand-blue-deep))] shadow-[0_0_20px_rgb(var(--brand-blue)/0.8)]" />
            <span className="absolute left-[35%] top-[65%] h-4 w-4 rounded-full bg-[rgb(var(--brand-blue))] shadow-[0_0_20px_rgb(var(--brand-blue)/0.8)]" />
            <span className="absolute left-[80%] top-[30%] h-4 w-4 rounded-full bg-[rgb(var(--brand-blue-deep))] shadow-[0_0_20px_rgb(var(--brand-blue)/0.8)]" />
            <span className="absolute left-[23%] top-[28%] h-[2px] w-[45%] origin-left rotate-[12deg] bg-gradient-to-r from-[rgb(var(--brand-blue))] to-transparent opacity-60" />
            <span className="absolute left-[36%] top-[50%] h-[2px] w-[32%] origin-left -rotate-[20deg] bg-gradient-to-r from-[rgb(var(--brand-blue))] to-transparent opacity-60" />
            <span className="absolute left-[60%] top-[58%] h-[2px] w-[22%] origin-left rotate-[25deg] bg-gradient-to-r from-[rgb(var(--brand-blue-deep))] to-transparent opacity-60" />
          </div>
        </div>

        <div>
          <h2 className="mb-7 font-bold text-white text-[clamp(2rem,4vw,2.5rem)]">
            Why Choose AutoAudit?
          </h2>
          {benefits.map((benefit) => (
            <article
              key={benefit.title}
              className="flex gap-4 items-start p-5 mb-3.5 rounded-2xl border transition duration-300 hover:translate-x-2 border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.02)] hover:border-[rgb(var(--brand-blue))] hover:shadow-[0_20px_45px_rgb(var(--brand-blue)/0.18)]"
            >
              <div className="flex justify-center items-center bg-gradient-to-br border h-[50px] w-[50px] shrink-0 rounded-[14px] border-[rgb(255_255_255/0.08)] from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))] text-[rgb(236_240_255/0.98)] shadow-[0_10px_22px_rgb(var(--brand-blue)/0.22)]">
                <benefit.icon size={18} strokeWidth={2.2} />
              </div>
              <div>
                <h3 className="mb-1.5 text-xl font-semibold text-white">{benefit.title}</h3>
                <p className="m-0 leading-relaxed text-[rgb(var(--landing-text-soft))]">{benefit.description}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;

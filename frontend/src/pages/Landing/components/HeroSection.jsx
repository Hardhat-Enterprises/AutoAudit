import React from "react";
import { Lock, Bolt, BarChart3 } from "lucide-react";

const floatingCards = [
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

const HeroSection = ({ onSignInClick }) => {
  return (
    <section className="bg-surface-1 text-text-strong py-24 px-6">
      <div className="max-w-6xl mx-auto grid gap-12 lg:grid-cols-2 items-center">

        {/* LEFT SIDE TEXT */}
        <div>
          <p className="text-accent-teal font-bold uppercase text-sm mb-3">
            AutoAudit Platform
          </p>

          <h1 className="text-5xl font-extrabold leading-tight mb-5 font-header">
            Access your compliance dashboard
            <br />
            and security insights.
          </h1>

          <p className="text-text-muted text-lg leading-relaxed max-w-xl mb-8">
            Compliance made easy for you. View your dashboards anytime,
            anywhere. Automate security monitoring and stay ahead of threats
            with real-time insights.
          </p>

          <div className="flex gap-4 flex-wrap">
            <button
              type="button"
              onClick={onSignInClick}
              className="px-5 py-3 bg-accent-teal text-surface-1 font-bold rounded-card shadow-elev-1 hover:bg-accent-teal/80 transition"
            >
              Get Started
            </button>

            <a
              href="#features"
              className="px-5 py-3 border border-border-subtle text-text-strong rounded-card hover:bg-surface-2 transition"
            >
              Learn More
            </a>
          </div>
        </div>

        {/* RIGHT SIDE FLOATING CARDS */}
        <div className="grid gap-6 sm:grid-cols-2">
          {floatingCards.map(({ icon: Icon, title, subtitle }) => (
            <article
              key={title}
              className="
                bg-surface-2
                border border-border-subtle
                rounded-card
                p-6
                shadow-elev-1
                transition
                hover:-translate-y-1
                hover:shadow-elev-2
              "
            >
              <div className="mb-4 text-accent-teal">
                <Icon size={20} strokeWidth={2.2} />
              </div>

              <h3 className="font-extrabold mb-2">
                {title}
              </h3>

              <p className="text-text-muted text-sm leading-relaxed">
                {subtitle}
              </p>
            </article>
          ))}
        </div>

      </div>
    </section>
  );
};

export default HeroSection;

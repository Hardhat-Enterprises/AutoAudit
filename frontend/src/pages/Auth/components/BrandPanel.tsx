import React from "react";
import { Lock, Zap, BarChart3, type LucideIcon } from "lucide-react";

const brandFeatures: { icon: LucideIcon; text: string }[] = [
  { icon: Lock, text: "Enterprise-grade security & encryption" },
  { icon: Zap, text: "Real-time compliance monitoring" },
  { icon: BarChart3, text: "Actionable reporting & insights" },
];

const particles = [
  { position: "left-[12%] top-[25%]", delay: "animate-[floatParticle_18s_infinite]" },
  { position: "left-[30%] top-[70%]", delay: "[animation-delay:2s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[52%] top-[45%]", delay: "[animation-delay:4s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[68%] top-[80%]", delay: "[animation-delay:1s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[82%] top-[35%]", delay: "[animation-delay:3s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[20%] top-[85%]", delay: "[animation-delay:5s] animate-[floatParticle_18s_infinite]" },
];

const BrandPanel = () => {
  return (
    <section
      className="flex overflow-hidden relative justify-center items-center py-10 px-12 text-white rounded-3xl max-lg:min-h-[60vh] max-sm:px-6"
      aria-labelledby="brand-title"
    >
      <style>{`
        @keyframes brandPulse {
          0%, 100% {
            transform: scale(1);
            opacity: 0.3;
          }
          50% {
            transform: scale(1.2);
            opacity: 0.7;
          }
        }

        @keyframes floatParticle {
          0%, 100% {
            transform: translate(0, 0);
            opacity: 0.4;
          }
          50% {
            transform: translate(25px, -60px);
            opacity: 0.8;
          }
        }
      `}</style>

      <span
        className="pointer-events-none absolute -right-40 -top-40 h-120 w-120 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.15)_0%,transparent_70%)] opacity-60 animate-[brandPulse_8s_ease-in-out_infinite]"
        aria-hidden="true"
      />
      <span
        className="pointer-events-none absolute -bottom-30 -left-30 h-90 w-90 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.15)_0%,transparent_70%)] opacity-60 [animation-delay:2s] animate-[brandPulse_8s_ease-in-out_infinite]"
        aria-hidden="true"
      />

      {particles.map((particle, index) => (
        <span
          key={index}
          className={`absolute h-1 w-1 rounded-full bg-[rgb(var(--brand-blue))] opacity-40 ${particle.position} ${particle.delay}`}
          aria-hidden="true"
        />
      ))}

      <div className="flex relative z-10 flex-col gap-6 items-center text-center max-w-105">
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img
            src="/AutoAudit.png"
            alt="AutoAudit"
            className="mb-4 h-auto w-45 drop-shadow-[0_10px_25px_rgb(var(--brand-blue)/0.3)]"
            loading="lazy"
          />
        </picture>

        <div id="brand-title">
          <h1 className="mb-4 font-bold text-transparent bg-clip-text bg-[linear-gradient(135deg,#ffffff,#3b82f6)] text-[clamp(1.8rem,4vw,2.3rem)]">
            Access security insights anywhere
          </h1>
          <p className="m-0 text-center leading-[1.6] text-[rgb(var(--landing-text-soft))]">
            Connect to your Microsoft 365 compliance dashboard, monitor security posture, and act on
            real-time recommendations.
          </p>
        </div>

        <div
          className="flex flex-col gap-4 mt-4 w-full max-lg:hidden"
          aria-label="Platform highlights"
        >
          {brandFeatures.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.text}
                className="flex gap-4 items-center p-4 text-left rounded-xl border border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)]"
              >
                <span
                  className="grid place-items-center w-10 h-10 rounded-[10px] bg-[linear-gradient(135deg,#3b82f6,#2563eb)]"
                  aria-hidden="true"
                >
                  <Icon size={18} strokeWidth={2.2} />
                </span>
                <span className="text-left">{feature.text}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default BrandPanel;
import React from "react";
import { BarChart3, Lock, Zap, type LucideIcon } from "lucide-react";

const featureItems: { icon: LucideIcon; text: string }[] = [
  { icon: Zap, text: "Setup in minutes, not hours" },
  { icon: Lock, text: "Bank-level security & encryption" },
  { icon: BarChart3, text: "Real-time compliance monitoring" },
];

const particles = [
  { position: "left-[12%] top-[25%]", delay: "animate-[floatParticle_18s_infinite]" },
  { position: "left-[30%] top-[70%]", delay: "[animation-delay:2s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[52%] top-[45%]", delay: "[animation-delay:4s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[68%] top-[80%]", delay: "[animation-delay:1s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[82%] top-[35%]", delay: "[animation-delay:3s] animate-[floatParticle_18s_infinite]" },
  { position: "left-[20%] top-[85%]", delay: "[animation-delay:5s] animate-[floatParticle_18s_infinite]" },
];

const SignupBrandPanel = () => {
  return (
    <section
      className="relative flex items-center justify-center overflow-hidden rounded-3xl px-12 py-10 text-white max-lg:min-h-[60vh] max-sm:px-6"
      aria-labelledby="signup-brand-title"
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
        className="pointer-events-none absolute -right-40 -top-40 h-120 w-120 rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.15)_0%,transparent_70%)] opacity-60 animate-[brandPulse_8s_ease-in-out_infinite]"
        aria-hidden="true"
      />
      <span
        className="pointer-events-none absolute -bottom-30 -left-30 h-90 w-90 rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.15)_0%,transparent_70%)] opacity-60 [animation-delay:2s] animate-[brandPulse_8s_ease-in-out_infinite]"
        aria-hidden="true"
      />

      {particles.map((particle, index) => (
        <span
          key={index}
          className={`absolute h-1 w-1 rounded-full bg-[#3b82f6] opacity-40 ${particle.position} ${particle.delay}`}
          aria-hidden="true"
        />
      ))}

      <div className="relative z-10 flex max-w-105 flex-col items-center gap-6 text-center">
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img
            src="/AutoAudit.png"
            alt="AutoAudit"
            className="mb-4 h-auto w-45 drop-shadow-[0_10px_25px_rgba(59,130,246,0.3)]"
            loading="lazy"
          />
        </picture>

        <div id="signup-brand-title">
          <h1 className="mb-4 bg-[linear-gradient(135deg,#ffffff,#3b82f6)] bg-clip-text text-[clamp(1.8rem,4vw,2.3rem)] font-bold text-transparent">
            Start Your Compliance Journey
          </h1>
          <p className="m-0 text-center leading-[1.6] text-[#b0c4de]">
            Join organizations that rely on AutoAudit to monitor, analyze, and improve their
            Microsoft 365 security posture.
          </p>
        </div>

        <div className="mt-4 flex w-full flex-col gap-4 max-lg:hidden" aria-label="AutoAudit highlights">
          {featureItems.map((item) => {
            const Icon = item.icon;
            return (
              <article
                key={item.text}
                className="flex items-center gap-4 rounded-xl border border-[rgba(59,130,246,0.1)] bg-[rgba(255,255,255,0.03)] p-4 text-left"
              >
                <span
                  className="grid h-10 w-10 place-items-center rounded-[10px] bg-[linear-gradient(135deg,#3b82f6,#2563eb)]"
                  aria-hidden="true"
                >
                  <Icon size={18} strokeWidth={2.2} />
                </span>
                <span className="text-left">{item.text}</span>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default SignupBrandPanel;
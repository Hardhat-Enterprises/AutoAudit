import React from "react";
import { Link } from "react-router-dom";

type CTASectionProps = {
  onSignInClick?: () => void;
};

const CTASection = ({ onSignInClick }: CTASectionProps) => {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-[rgb(var(--landing-bg-base))] via-[rgb(var(--landing-bg-mid))] to-[rgb(var(--landing-bg-end))] px-[5%] py-24 text-center">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgb(var(--brand-blue)/0.08),transparent_62%),radial-gradient(circle_at_88%_22%,rgb(var(--brand-blue-deep)/0.06),transparent_60%)]" />
      <div className="relative mx-auto max-w-[760px]">
        <h2 className="mb-4 font-bold text-white text-[clamp(2rem,4vw,2.75rem)]">
          Ready to transform your compliance process?
        </h2>
        <p className="mb-8 leading-relaxed text-[1.2rem] text-[rgb(var(--landing-text-soft))]">
          Join thousands of organizations that trust AutoAudit to keep their
          Microsoft 365 environment secure and compliant.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            type="button"
            className="inline-flex justify-center items-center py-3 px-7 font-semibold text-white bg-gradient-to-br rounded-full transition duration-200 hover:-translate-y-0.5 from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))] shadow-[0_8px_30px_rgb(var(--brand-blue)/0.35)] hover:shadow-[0_12px_30px_rgb(var(--brand-blue)/0.5)]"
            onClick={onSignInClick}
          >
            Start Free Trial
          </button>
          <Link
            className="inline-flex justify-center items-center py-3 px-7 font-semibold rounded-full border-2 transition duration-200 hover:-translate-y-0.5 border-[rgb(var(--brand-blue))] text-[rgb(var(--brand-blue))] hover:bg-[rgb(var(--brand-blue))] hover:text-[rgb(var(--landing-bg-base))]"
            to="/contact"
          >
            Schedule Demo
          </Link>
        </div>
      </div>
    </section>
  );
};

export default CTASection;

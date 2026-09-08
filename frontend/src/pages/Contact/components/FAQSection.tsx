import React, { useState } from "react";

type FAQ = {
  question: string;
  answer: string;
};

type FAQItemProps = FAQ & {
  isActive: boolean;
  onToggle: () => void;
};

// Data
const faqItems: FAQ[] = [
  {
    question: "How quickly can I get started with AutoAudit?",
    answer:
      "You can be up and running in minutes. Simply sign up, connect your Microsoft 365 tenant using our secure OAuth integration, and start your first compliance scan immediately. No installation or complex setup required.",
  },
  {
    question: "What compliance frameworks does AutoAudit support?",
    answer:
      "AutoAudit assesses supported CIS Microsoft 365 Foundations controls. These findings can inform a broader compliance review; they do not establish SOC 2, ISO 27001, NIST, or GDPR compliance.",
  },
  {
    question: "Is my data secure with AutoAudit?",
    answer:
      "AutoAudit processes configuration and evidence data to produce assessment results. Security depends on how the service is deployed and operated. AutoAudit does not claim SOC 2 certification or an independent security audit. Review your deployment and data-handling requirements before connecting a tenant.",
  },
  // There is no billing system, no plan tier and no trial: nothing in the
  // product distinguishes one account's entitlements from another's. The
  // export answer promised PDF, Excel and CSV; the only report the product
  // generates is a plain-text file per evidence scan.
  {
    question: "Is there a paid plan or a trial?",
    answer:
      "Not yet. AutoAudit has no billing, plan tiers or trial system; every account has the same access. Contact us if you want to discuss how it would be run for your organisation.",
  },
  {
    question: "What kind of support do you provide?",
    answer:
      "Contact us through the form on this page. There are no support tiers or service commitments to describe yet.",
  },
  {
    question: "Can I export compliance reports?",
    answer:
      "Each evidence scan produces a downloadable report: a PDF, or a DOCX or plain-text file when the PDF converter is unavailable. There is no Excel or CSV export.",
  },
];

const FAQItem: React.FC<FAQItemProps> = ({
  question,
  answer,
  isActive,
  onToggle,
}) => (
  <article className="overflow-hidden mb-4 border rounded-[15px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.02)]">
    <button
      className="flex justify-between items-center py-5 px-6 w-full text-base text-left text-white bg-transparent transition hover:bg-[rgb(255_255_255/0.04)]"
      type="button"
      onClick={onToggle}
    >
      <span className="pr-4 font-medium">{question}</span>
      <span
        className={`text-[1.4rem] text-[rgb(var(--brand-blue))] transition-transform duration-300 ${
          isActive ? "rotate-45" : ""
        }`}
      >
        +
      </span>
    </button>

    <div
      className={`overflow-hidden transition-all duration-300 ${
        isActive ? "max-h-[500px]" : "max-h-0"
      }`}
    >
      <div className="px-6 pb-6 text-[rgb(var(--landing-text-soft))] leading-[1.6]">{answer}</div>
    </div>
  </article>
);

const FAQSection: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  return (
    <section
      id="benefits"
      className="bg-gradient-to-br from-[rgb(var(--landing-bg-base))] to-[rgb(var(--landing-bg-alt-start))] px-[5%] py-24"
    >
      <div className="mx-auto max-w-[900px]">
        <div className="mb-10 text-center">
          <h2 className="mb-3 font-semibold text-white text-[2.4rem]">
            Frequently Asked Questions
          </h2>
          <p className="text-[rgb(var(--landing-text-soft))]">
            Quick answers to common questions about AutoAudit
          </p>
        </div>

        {faqItems.map((item, index) => (
          <FAQItem
            key={item.question}
            {...item}
            isActive={activeIndex === index}
            onToggle={() =>
              setActiveIndex(activeIndex === index ? null : index)
            }
          />
        ))}
      </div>
    </section>
  );
};

export default FAQSection;

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
      "AutoAudit supports CIS Microsoft 365 Foundations Benchmark, NIST Cybersecurity Framework, ISO 27001, SOC 2, and GDPR compliance requirements. We continuously update our benchmarks to align with the latest security standards.",
  },
  {
    question: "Is my data secure with AutoAudit?",
    answer:
      "Absolutely. We use bank-level encryption, zero-knowledge architecture, and follow strict security protocols. Your data is encrypted in transit and at rest. We're SOC 2 Type II certified and undergo regular third-party security audits.",
  },
  {
    question: "Do you offer a free trial?",
    answer:
      "Yes! We offer a 14-day free trial with full access to all features. No credit card required. Experience the power of automated compliance monitoring risk-free.",
  },
  {
    question: "What kind of support do you provide?",
    answer:
      "We provide email and chat support for all customers. Premium and Enterprise plans include priority support, dedicated account managers, and 24/7 emergency assistance. We also offer comprehensive documentation and video tutorials.",
  },
  {
    question: "Can I export compliance reports?",
    answer:
      "Yes! Generate and export comprehensive compliance reports in PDF, Excel, or CSV formats. Reports are audit-ready and can be customized to meet your specific regulatory requirements.",
  },
];

const FAQItem: React.FC<FAQItemProps> = ({
  question,
  answer,
  isActive,
  onToggle,
}) => (
  <article className="mb-4 overflow-hidden rounded-[15px] border border-[rgba(59,130,246,0.1)] bg-[rgba(255,255,255,0.02)]">
    <button
      className="flex w-full items-center justify-between bg-transparent px-6 py-5 text-left text-base text-white transition hover:bg-[rgba(255,255,255,0.04)]"
      type="button"
      onClick={onToggle}
    >
      <span className="pr-4 font-medium">{question}</span>
      <span
        className={`text-[1.4rem] text-[#3b82f6] transition-transform duration-300 ${
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
      <div className="px-6 pb-6 text-[#b0c4de] leading-[1.6]">{answer}</div>
    </div>
  </article>
);

const FAQSection: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  return (
    <section
      id="benefits"
      className="bg-gradient-to-br from-[#0a1628] to-[#1e3a5f] px-[5%] py-24"
    >
      <div className="mx-auto max-w-[900px]">
        <div className="mb-10 text-center">
          <h2 className="mb-3 text-[2.4rem] font-semibold text-white">
            Frequently Asked Questions
          </h2>
          <p className="text-[#b0c4de]">
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

import React, { useState } from "react";

const faqItems = [
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

const FAQItem = ({ question, answer, isActive, onToggle }) => (
  <article className={`faq-item ${isActive ? "active" : ""}`}>
    <button className="faq-question" type="button" onClick={onToggle}>
      <span>{question}</span>
      <span className="faq-icon">+</span>
    </button>
    <div className="faq-answer">
      <div className="faq-answer-content">{answer}</div>
    </div>
  </article>
);

const FAQSection = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  return (
    <section className="faq-section" id="benefits">
      <div className="faq-container">
        <div className="faq-header">
          <h2>Frequently Asked Questions</h2>
          <p>Quick answers to common questions about AutoAudit</p>
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

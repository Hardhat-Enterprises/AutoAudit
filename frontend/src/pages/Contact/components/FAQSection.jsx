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

const highlight = (text, query) => {
  if (!query.trim()) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part) ? <mark key={i} className="faq-highlight">{part}</mark> : part
  );
};

const FAQItem = ({ question, answer, isActive, onToggle, searchQuery, feedback, onFeedback }) => (
  <article className={`faq-item ${isActive ? "active" : ""}`}>
    <button className="faq-question" type="button" onClick={onToggle}>
      <span>{highlight(question, searchQuery)}</span>
      <span className="faq-icon">+</span>
    </button>
    <div className="faq-answer">
      <div className="faq-answer-content">
        <p>{highlight(answer, searchQuery)}</p>
        <div className="faq-feedback">
          <span className="faq-feedback-label">Was this helpful?</span>
          <button
            className={`faq-feedback-btn ${feedback === "yes" ? "active" : ""}`}
            onClick={() => onFeedback("yes")}
            aria-label="Yes, this was helpful"
          >
            👍
          </button>
          <button
            className={`faq-feedback-btn ${feedback === "no" ? "active" : ""}`}
            onClick={() => onFeedback("no")}
            aria-label="No, this was not helpful"
          >
            👎
          </button>
          {feedback && (
            <span className="faq-feedback-thanks">
              {feedback === "yes" ? "Glad it helped!" : "Thanks for the feedback!"}
            </span>
          )}
        </div>
      </div>
    </div>
  </article>
);

const FAQSection = () => {
  const [activeIndex, setActiveIndex] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  // feedback is session-only (in-memory), resets on page refresh
  const [feedbacks, setFeedbacks] = useState({});

  const filtered = faqItems.filter(
    ({ question, answer }) =>
      question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleFeedback = (index, value) => {
    setFeedbacks((prev) => ({ ...prev, [index]: value }));
  };

  return (
    <section className="faq-section" id="benefits">
      <div className="faq-container">
        <div className="faq-header">
          <h2>Frequently Asked Questions</h2>
          <p>Quick answers to common questions about AutoAudit</p>
        </div>

        <div className="faq-search-wrapper">
          <input
            type="text"
            className="faq-search"
            placeholder="Search questions..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setActiveIndex(null);
            }}
            aria-label="Search frequently asked questions"
          />
          {searchQuery && (
            <button className="faq-search-clear" onClick={() => setSearchQuery("")} aria-label="Clear search">
              ✕
            </button>
          )}
        </div>

        {filtered.length > 0 ? (
          filtered.map((item, index) => {
            const originalIndex = faqItems.indexOf(item);
            return (
              <FAQItem
                key={item.question}
                {...item}
                searchQuery={searchQuery}
                isActive={activeIndex === index}
                onToggle={() => setActiveIndex(activeIndex === index ? null : index)}
                feedback={feedbacks[originalIndex]}
                onFeedback={(value) => handleFeedback(originalIndex, value)}
              />
            );
          })
        ) : (
          <p className="faq-no-results">No results found for "{searchQuery}"</p>
        )}
      </div>
    </section>
  );
};

export default FAQSection;

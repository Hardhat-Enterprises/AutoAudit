import React, { useState } from "react";
import "./ContactPage.css";
import "../Landing/LandingPage.css";
import LandingHeader from "../Landing/components/LandingHeader";
import LandingFooter from "../Landing/components/LandingFooter";
import ContactInfoGrid from "./components/ContactInfoGrid";
import ContactForm from "./components/ContactForm";
import FAQSection from "./components/FAQSection";

const ContactHero = () => (
  <section className="contact-hero" id="home">
    <div className="contact-hero-content">
      <p className="section-tag">Contact AutoAudit</p>
      <h1>Get in Touch</h1>
      <p>
        Have questions about AutoAudit? Our team is here to help. Reach out and
        we&apos;ll respond as soon as possible.
      </p>
    </div>
  </section>
);

const ContactPage = ({ onSignIn }) => {
  const [submitted, setSubmitted] = useState(false);

  const handleFormSuccess = () => {
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <div className="contact-page">
      <LandingHeader onSignInClick={onSignIn} />
      <main>
        <ContactHero />

        <section className="contact-section" id="features">
          <div className="contact-container">
            <ContactInfoGrid />
            <ContactForm submitted={submitted} onSuccess={handleFormSuccess} />
          </div>
        </section>

        <FAQSection />
      </main>
      <LandingFooter />
    </div>
  );
};

export default ContactPage;

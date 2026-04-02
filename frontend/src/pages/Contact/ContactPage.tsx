import React, { useState } from "react";
import "../Landing/LandingPage.css";
import LandingHeader from "../Landing/components/LandingHeader";
import LandingFooter from "../Landing/components/LandingFooter";
import ContactInfoGrid from "./components/ContactInfoGrid";
import ContactForm from "./components/ContactForm";
import FAQSection from "./components/FAQSection";
import { createContactSubmission } from "../../api/client";

type ContactFormPayload = {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string | null;
  company?: string | null;
  subject: string;
  message: string;
};

type ContactPageProps = {
  onSignIn?: () => void;
};

const ContactHero: React.FC = () => (
  <section
    id="home"
    className="relative overflow-hidden bg-gradient-to-br from-[#0a1628] via-[#162a4a] to-[#1e3a5f] px-[5%] pb-16 pt-40 text-center"
  >
    <div className="pointer-events-none absolute -right-[200px] -top-[200px] h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.1)_0%,transparent_70%)] opacity-90" />
    <div className="pointer-events-none absolute -bottom-[100px] -left-[100px] h-[400px] w-[400px] rounded-full bg-[radial-gradient(circle,rgba(59,130,246,0.1)_0%,transparent_70%)] opacity-90" />

    <div className="relative z-[1] mx-auto max-w-[800px]">
      <p className="section-tag">Contact AutoAudit</p>
      <h1 className="mb-4 bg-gradient-to-br from-white to-[#3b82f6] bg-clip-text text-[clamp(2.5rem,6vw,3.5rem)] font-bold text-transparent">
        Get in Touch
      </h1>
      <p className="text-[1.2rem] leading-[1.6] text-[#b0c4de]">
        Have questions about AutoAudit? Our team is here to help. Reach out and
        we&apos;ll respond as soon as possible.
      </p>
    </div>
  </section>
);

const ContactPage: React.FC<ContactPageProps> = ({ onSignIn }) => {
  const [submitted, setSubmitted] = useState<boolean>(false);

  const handleFormSuccess = () => {
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
  };

  const handleSubmit = async (payload: ContactFormPayload) => {
    await createContactSubmission({
      first_name: payload.firstName,
      last_name: payload.lastName,
      email: payload.email,
      phone: payload.phone || null,
      company: payload.company || null,
      subject: payload.subject,
      message: payload.message,
      source: "website",
    });
    handleFormSuccess();
  };

  return (
    <div className="min-h-screen bg-[#0a1628] font-['Inter',-apple-system,BlinkMacSystemFont,'Segoe_UI',sans-serif] text-white">
      <LandingHeader onSignInClick={onSignIn} />

      <main className="flex flex-col">
        <ContactHero />

        <section id="features" className="bg-[#0f1f38] px-[5%] py-24">
          <div className="mx-auto grid max-w-[1200px] gap-12 lg:grid-cols-[1fr_1.8fr] items-start">
            <ContactInfoGrid />
            <ContactForm submitted={submitted} onSubmit={handleSubmit} />
          </div>
        </section>

        <FAQSection />
      </main>

      <LandingFooter />
    </div>
  );
};

export default ContactPage;

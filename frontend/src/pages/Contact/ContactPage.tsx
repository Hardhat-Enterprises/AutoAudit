import React, { useState } from "react";
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
    className="relative overflow-hidden bg-linear-to-br from-surface-1 via-accent-navy/88 to-accent-navy/70 px-[5%] pb-16 pt-40 text-center"
  >
    <div className="pointer-events-none absolute -right-50 -top-50 h-150 w-150 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.1)_0%,transparent_70%)] opacity-90" />
    <div className="pointer-events-none absolute -bottom-25 -left-25 h-100 w-100 rounded-full bg-[radial-gradient(circle,rgb(var(--brand-blue)/0.1)_0%,transparent_70%)] opacity-90" />

    <div className="relative mx-auto z-1 max-w-200">
      <p className="mb-3 text-sm font-semibold tracking-wide text-text-strong">
        Contact AutoAudit
      </p>
      <h1 className="mb-4 font-bold text-transparent bg-clip-text bg-linear-to-br from-text-strong to-brand-blue text-[clamp(2.5rem,6vw,3.5rem)]">
        Get in Touch
      </h1>
      <p className="text-[1.2rem] leading-[1.6] text-text-muted">
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
    <div className="min-h-screen bg-dark-surface-1 font-['Inter',-apple-system,BlinkMacSystemFont,'Segoe_UI',sans-serif] text-text-strong">
      <LandingHeader onSignInClick={onSignIn} />

      <main className="flex flex-col">
        <ContactHero />

        <section id="features" className="bg-accent-navy/82 px-[5%] py-24">
          <div className="grid gap-12 items-start mx-auto max-w-300 lg:grid-cols-[1fr_1.8fr]">
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

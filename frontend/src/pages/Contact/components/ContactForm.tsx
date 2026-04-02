import React, { useState, ChangeEvent, FormEvent } from "react";

type ContactFormData = {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  company?: string;
  subject: string;
  message: string;
};

type ContactFormProps = {
  submitted: boolean;
  onSubmit: (data: ContactFormData) => Promise<void>;
};

// Initial state
const initialState: ContactFormData = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  company: "",
  subject: "",
  message: "",
};

const fieldClassName =
  "w-full rounded-xl border border-[rgba(59,130,246,0.2)] bg-[rgba(255,255,255,0.05)] px-4 py-4 text-base text-white outline-none transition duration-200 placeholder:text-slate-400 focus:border-[#3b82f6] focus:bg-[rgba(255,255,255,0.08)] focus:shadow-[0_0_0_2px_rgba(59,130,246,0.15)]";

const labelClassName = "mb-2 block text-sm font-medium text-[#b0c4de]";

const ContactForm: React.FC<ContactFormProps> = ({ submitted, onSubmit }) => {
  const [formData, setFormData] = useState<ContactFormData>(initialState);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  // Handle input changes
  const handleChange = (
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError("");
  };

  // Handle form submit
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      setFormData(initialState);
    } catch (err: any) {
      setError(err?.message || "Unable to send message right now.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="rounded-[20px] border border-[rgba(59,130,246,0.1)] bg-[rgba(255,255,255,0.03)] p-8 backdrop-blur-[10px] md:p-12">
      <h2 className="mb-6 text-2xl font-semibold text-white">
        Send us a Message
      </h2>

      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2">
          <div>
            <label htmlFor="firstName" className={labelClassName}>
              First Name *
            </label>
            <input
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              className={fieldClassName}
            />
          </div>

          <div>
            <label htmlFor="lastName" className={labelClassName}>
              Last Name *
            </label>
            <input
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              className={fieldClassName}
            />
          </div>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2">
          <div>
            <label htmlFor="email" className={labelClassName}>
              Email Address *
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={fieldClassName}
            />
          </div>

          <div>
            <label htmlFor="phone" className={labelClassName}>
              Phone Number
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              className={fieldClassName}
            />
          </div>
        </div>

        <div className="mb-6">
          <label htmlFor="company" className={labelClassName}>
            Company Name
          </label>
          <input
            id="company"
            name="company"
            value={formData.company}
            onChange={handleChange}
            className={fieldClassName}
          />
        </div>

        <div className="mb-6">
          <label htmlFor="subject" className={labelClassName}>
            Subject *
          </label>
          <select
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            className={fieldClassName}
          >
            <option value="">Select a subject</option>
            <option value="general">General Inquiry</option>
            <option value="sales">Sales Question</option>
            <option value="support">Technical Support</option>
            <option value="partnership">Partnership Opportunity</option>
            <option value="demo">Request a Demo</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="mb-6">
          <label htmlFor="message" className={labelClassName}>
            Message *
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            className={`${fieldClassName} min-h-[150px] resize-y`}
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-2 w-full rounded-full bg-gradient-to-br from-[#3b82f6] to-[#2563eb] px-6 py-3 text-lg font-semibold text-white transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_10px_25px_rgba(59,130,246,0.35)] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? "Sending..." : "Send Message"}
        </button>

        {error && (
          <div className="mt-4 rounded-xl border border-[rgba(239,68,68,0.4)] bg-[rgba(239,68,68,0.12)] px-4 py-3 text-center text-[#fecaca]">
            {error}
          </div>
        )}

        {submitted && (
          <div className="mt-4 rounded-xl border border-[#3b82f6] bg-[rgba(59,130,246,0.12)] px-4 py-4 text-center text-[#3b82f6]">
            ✓ Thank you! Your message has been sent successfully. We&apos;ll get
            back to you soon.
          </div>
        )}
      </form>
    </div>
  );
};

export default ContactForm;

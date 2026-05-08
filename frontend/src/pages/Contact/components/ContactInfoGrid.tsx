import React from "react";
import {
  Twitter,
  Linkedin,
  Facebook,
  Instagram,
  LucideIcon,
} from "lucide-react";

// Type for links and social icons
type ContactLink = {
  label: string;
  href: string;
};

type SocialLink = {
  label: string;
  icon: LucideIcon; // Lucide-react icon type
  href: string;
};

type InfoCard = {
  icon: string;
  title: string;
  description: string;
  links?: ContactLink[];
  social?: SocialLink[];
};

// Data
const infoCards: InfoCard[] = [
  {
    icon: "📧",
    title: "Email Us",
    description: "Our team typically responds within 24 hours",
    links: [
      { label: "support@autoaudit.com", href: "mailto:support@autoaudit.com" },
      { label: "sales@autoaudit.com", href: "mailto:sales@autoaudit.com" },
    ],
  },
  {
    icon: "📞",
    title: "Call Us",
    description: "Monday - Friday, 9am - 6pm EST",
    links: [
      { label: "+1 (234) 567-890", href: "tel:+1234567890" },
      { label: "+1 (234) 567-891", href: "tel:+1234567891" },
    ],
  },
  {
    icon: "📍",
    title: "Visit Us",
    description: `221 Burwood Highway
Burwood, VIC 3125
Australia`,
  },
  {
    icon: "🌐",
    title: "Follow Us",
    description: "Stay connected on social media",
    social: [
      { label: "Twitter", icon: Twitter, href: "#" },
      { label: "LinkedIn", icon: Linkedin, href: "#" },
      { label: "Facebook", icon: Facebook, href: "#" },
      { label: "Instagram", icon: Instagram, href: "#" },
    ],
  },
];

const ContactInfoGrid: React.FC = () => {
  return (
    <div className="flex flex-col gap-6">
      {infoCards.map((card) => (
        <article
          key={card.title}
          className="p-8 border transition-all duration-300 rounded-[20px] border-[rgb(var(--brand-blue)/0.1)] bg-[rgb(255_255_255/0.03)] hover:border-[rgb(var(--brand-blue))] hover:bg-[rgb(255_255_255/0.05)]"
        >
          <div className="flex justify-center items-center mb-5 text-2xl bg-gradient-to-br h-[56px] w-[56px] rounded-[14px] from-[rgb(var(--brand-blue))] to-[rgb(var(--brand-blue-deep))]">
            {card.icon}
          </div>

          <h3 className="mb-2 text-xl font-semibold text-white">
            {card.title}
          </h3>

          <p className="mb-2 whitespace-pre-line leading-[1.6] text-[rgb(var(--landing-text-soft))]">
            {card.description}
          </p>

          {card.links &&
            card.links.map((link, index) => (
              <a
                key={`${link.label}-${index}`}
                href={link.href}
                className="block transition text-[rgb(var(--brand-blue))] hover:text-[rgb(var(--brand-blue-deep))]"
              >
                {link.label}
              </a>
            ))}

          {card.social && (
            <div className="flex gap-4 mt-4">
              {card.social.map(({ label, icon: Icon, href }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  className="flex justify-center items-center text-white border transition hover:bg-gradient-to-br hover:border-transparent h-[44px] w-[44px] rounded-[12px] border-[rgb(var(--brand-blue)/0.2)] bg-[rgb(var(--brand-blue)/0.12)] hover:from-[rgb(var(--brand-blue))] hover:to-[rgb(var(--brand-blue-deep))]"
                >
                  <Icon size={18} strokeWidth={1.7} />
                </a>
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  );
};

export default ContactInfoGrid;

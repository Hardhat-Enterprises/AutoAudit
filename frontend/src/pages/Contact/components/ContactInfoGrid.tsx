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
          className="rounded-[20px] border border-[rgba(59,130,246,0.1)] bg-[rgba(255,255,255,0.03)] p-8 transition-all duration-300 hover:border-[#3b82f6] hover:bg-[rgba(255,255,255,0.05)]"
        >
          <div className="mb-5 flex h-[56px] w-[56px] items-center justify-center rounded-[14px] bg-gradient-to-br from-[#3b82f6] to-[#2563eb] text-2xl">
            {card.icon}
          </div>

          <h3 className="mb-2 text-xl font-semibold text-white">
            {card.title}
          </h3>

          <p className="mb-2 whitespace-pre-line leading-[1.6] text-[#b0c4de]">
            {card.description}
          </p>

          {card.links &&
            card.links.map((link, index) => (
              <a
                key={`${link.label}-${index}`}
                href={link.href}
                className="block text-[#3b82f6] transition hover:text-[#2563eb]"
              >
                {link.label}
              </a>
            ))}

          {card.social && (
            <div className="mt-4 flex gap-4">
              {card.social.map(({ label, icon: Icon, href }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  className="flex h-[44px] w-[44px] items-center justify-center rounded-[12px] border border-[rgba(59,130,246,0.2)] bg-[rgba(59,130,246,0.12)] text-white transition hover:border-transparent hover:bg-gradient-to-br hover:from-[#3b82f6] hover:to-[#2563eb]"
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

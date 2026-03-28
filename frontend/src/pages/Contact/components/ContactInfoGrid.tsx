
import React from "react";
import { Twitter, Linkedin, Facebook, Instagram, LucideIcon } from "lucide-react";

// Type for links and social icons
type ContactLink = {
  label: string;
  href: string;
}

type SocialLink = {
  label: string;
  icon: LucideIcon; // Lucide-react icon type
  href: string;
}

type InfoCard = {
  icon: string;
  title: string;
  description: string;
  links?: ContactLink[];
  social?: SocialLink[];
}

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
    <div className="contact-info">
      {infoCards.map((card) => (
        <article key={card.title} className="info-card">
          <div className="info-icon">{card.icon}</div>
          <h3>{card.title}</h3>
          <p>{card.description}</p>

          {card.links &&
            card.links.map((link, index) => (
              <a
                key={`${link.label}-${index}`}
                href={link.href}
                className="contact-link"
              >
                {link.label}
              </a>
            ))}

          {card.social && (
            <div className="social-links">
              {card.social.map(({ label, icon: Icon, href }) => (
                <a
                  key={label}
                  href={href}
                  className="social-link"
                  aria-label={label}
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
import React from "react";
import { Link } from "react-router-dom";

type FooterLink = {
  label: string;
  href: string;
};

type FooterColumn = {
  title: string;
  links: FooterLink[];
};

const footerColumns: FooterColumn[] = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#" },
      { label: "Integrations", href: "#" },
      { label: "Security", href: "#" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "#" },
      { label: "API Reference", href: "#" },
      { label: "Blog", href: "#" },
      { label: "Case Studies", href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About Us", href: "/about" },
      { label: "Careers", href: "#" },
      { label: "Contact", href: "/contact" },
      { label: "Partners", href: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Cookie Policy", href: "#" },
      { label: "Compliance", href: "#" },
    ],
  },
];

const LandingFooter = () => {
  return (
    <footer className="relative overflow-hidden border-t border-[rgb(var(--brand-blue)/0.1)] bg-linear-to-br from-landing-bg-base via-landing-bg-mid to-landing-bg-end px-[5%] pb-10 pt-16">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgb(var(--brand-blue)/0.08),transparent_62%),radial-gradient(circle_at_88%_22%,rgb(var(--brand-blue-deep)/0.06),transparent_60%)]" />
      <div className="grid relative gap-8 mx-auto mb-8 max-w-300 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">
        {footerColumns.map((column) => (
          <section key={column.title}>
            <h3 className="mb-4 text-lg font-semibold text-white">{column.title}</h3>
            <ul className="p-0 m-0 list-none">
              {column.links.map((link) => (
                <li key={link.label} className="mt-3 first:mt-0">
                  {link.href === "#" ? (
                    <span
                      className="cursor-not-allowed text-[rgb(var(--landing-text-soft)/0.45)]"
                      aria-disabled="true"
                    >
                      {link.label}
                    </span>
                  ) : link.href.startsWith("/") ? (
                    <Link className="transition-colors duration-200 text-landing-text-soft hover:text-brand-blue" to={link.href}>
                      {link.label}
                    </Link>
                  ) : link.href.startsWith("#") ? (
                    <Link className="transition-colors duration-200 text-landing-text-soft hover:text-brand-blue" to={`/${link.href}`}>
                      {link.label}
                    </Link>
                  ) : (
                    <a className="transition-colors duration-200 text-landing-text-soft hover:text-brand-blue" href={link.href}>
                      {link.label}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      <div className="relative pt-6 text-sm text-center border-t border-[rgb(var(--brand-blue)/0.1)] text-landing-text-soft">
        <p>&copy; {new Date().getFullYear()} AutoAudit. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default LandingFooter;

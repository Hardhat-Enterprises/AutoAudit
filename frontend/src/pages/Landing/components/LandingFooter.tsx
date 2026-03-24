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
    <footer className="landing-footer">
      <div className="footer-content">
        {footerColumns.map((column) => (
          <section key={column.title} className="footer-section">
            <h3>{column.title}</h3>
            <ul>
              {column.links.map((link) => (
                <li key={link.label}>
                  {link.href === "#" ? (
                    <span className="footer-link-disabled" aria-disabled="true">
                      {link.label}
                    </span>
                  ) : link.href.startsWith("/") ? (
                    <Link to={link.href}>{link.label}</Link>
                  ) : link.href.startsWith("#") ? (
                    <Link to={`/${link.href}`}>{link.label}</Link>
                  ) : (
                    <a href={link.href}>{link.label}</a>
                  )}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} AutoAudit. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default LandingFooter;

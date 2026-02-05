import React from "react";

const footerColumns = [
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
    <footer className="bg-surface-2 border-t border-border-subtle mt-24">
      <div className="max-w-6xl mx-auto px-6 py-16 grid gap-10 sm:grid-cols-2 md:grid-cols-4">
        {footerColumns.map((column) => (
          <section key={column.title}>
            <h3 className="text-text-strong font-semibold mb-4">
              {column.title}
            </h3>
            <ul className="space-y-2">
              {column.links.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-text-muted hover:text-accent-teal transition text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <div className="border-t border-border-subtle text-center py-6 text-text-muted text-sm">
        &copy; {new Date().getFullYear()} AutoAudit. All rights reserved.
      </div>
    </footer>
  );
};

export default LandingFooter;

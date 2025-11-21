import React from "react";

const footerColumns = [
  {
    title: "Product",
    links: ["Features", "Pricing", "Integrations", "Security"],
  },
  {
    title: "Resources",
    links: ["Documentation", "API Reference", "Blog", "Case Studies"],
  },
  {
    title: "Company",
    links: ["About Us", "Careers", "Contact", "Partners"],
  },
  {
    title: "Legal",
    links: ["Privacy Policy", "Terms of Service", "Cookie Policy", "Compliance"],
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
                <li key={link}>
                  <a href="#">{link}</a>
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

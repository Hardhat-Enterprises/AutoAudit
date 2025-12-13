import React from "react";

const navLinks = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const LandingHeader = ({ onSignInClick, hiddenLinks = [], showSignIn = true }) => {
  return (
    <header className="landing-header">
      <a className="landing-logo" href="/" aria-label="AutoAudit home">
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img src="/AutoAudit.png" alt="AutoAudit" loading="lazy" />
        </picture>
      </a>

      <nav className="landing-nav" aria-label="Primary navigation">
        {navLinks
          .filter((link) => !hiddenLinks.map((l) => l.toLowerCase()).includes(link.label.toLowerCase()))
          .map((link) => (
            <a key={link.label} href={link.href}>
              {link.label}
            </a>
          ))}
        {showSignIn && (
          <button
            type="button"
            className="btn-primary"
            onClick={onSignInClick}
          >
            Sign In
          </button>
        )}
      </nav>
    </header>
  );
};

export default LandingHeader;

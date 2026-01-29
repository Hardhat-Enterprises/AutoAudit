import React, { useState } from "react";

const navLinks = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const LandingHeader = ({ onSignInClick, hiddenLinks = [], showSignIn = true }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const visibleLinks = navLinks.filter(
    (link) =>
      !hiddenLinks.map((l) => l.toLowerCase()).includes(link.label.toLowerCase())
  );

  return (
    <header className="landing-header">
      <a className="landing-logo" href="/" aria-label="AutoAudit home">
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img src="/AutoAudit.png" alt="AutoAudit" loading="lazy" />
        </picture>
      </a>

      {/* Desktop nav */}
      <nav className="landing-nav desktop-nav" aria-label="Primary navigation">
        {visibleLinks.map((link) => (
          <a key={link.label} href={link.href}>
            {link.label}
          </a>
        ))}
        {showSignIn && (
          <button className="btn-primary" onClick={onSignInClick}>
            Sign In
          </button>
        )}
      </nav>

      {/* Hamburger toggle */}
      <button
        className="hamburger"
        aria-label="Toggle menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(!menuOpen)}
      >
        ☰
      </button>

      {/* Mobile menu */}
      {menuOpen && (
        <nav className="mobile-nav" aria-label="Mobile navigation">
          {visibleLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}

          {showSignIn && (
            <button
              className="btn-primary"
              onClick={() => {
                setMenuOpen(false);
                onSignInClick?.();
              }}
            >
              Sign In
            </button>
          )}
        </nav>
      )}
    </header>
  );
};

export default LandingHeader;

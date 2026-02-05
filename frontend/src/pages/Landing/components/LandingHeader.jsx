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
    <header className="bg-surface-1 border-b border-border-subtle px-6 py-4 flex items-center justify-between">
      <a
        href="/"
        aria-label="AutoAudit home"
        className="flex items-center"
      >
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img
            src="/AutoAudit.png"
            alt="AutoAudit"
            loading="lazy"
            className="h-10 rounded-card shadow-elev-1"
          />
        </picture>
      </a>

      <nav className="flex items-center gap-6" aria-label="Primary navigation">
        {navLinks
          .filter(
            (link) =>
              !hiddenLinks
                .map((l) => l.toLowerCase())
                .includes(link.label.toLowerCase())
          )
          .map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-text-strong font-medium opacity-90 hover:opacity-100 hover:text-accent-teal transition"
            >
              {link.label}
            </a>
          ))}

        {showSignIn && (
          <button
            type="button"
            onClick={onSignInClick}
            className="px-4 py-2 bg-accent-teal text-surface-1 font-semibold rounded-card shadow-elev-1 hover:bg-accent-teal/80 transition"
          >
            Sign In
          </button>
        )}
      </nav>
    </header>
  );
};

export default LandingHeader;

import React, { useState } from "react";

const navLinks = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const LoginHeader = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="auth-header">
      <a className="auth-logo" href="/" aria-label="AutoAudit home">
        <img src="/AutoAudit.png" alt="AutoAudit" />
      </a>

      {/* Desktop Header */}
      <nav className="auth-nav" aria-label="Primary navigation">
        {navLinks.map((link) => (
          <a key={link.label} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>

      <button
        className="auth-hamburger"
        aria-label="Toggle menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((prev) => !prev)}
      >
        ☰
      </button>

      {/* Mobile menu */}
      {menuOpen && (
        <nav className="auth-mobile-nav" aria-label="Auth Mobile navigation">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
        </nav>
      )}

    </header>
  );
};

export default LoginHeader;

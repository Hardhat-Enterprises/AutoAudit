import React from "react";

const navLinks = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const LoginHeader = () => {
  return (
    <header className="auth-header">
      <a className="auth-logo" href="/" aria-label="AutoAudit home">
        <img src="/AutoAudit.png" alt="AutoAudit" />
      </a>

      <nav className="auth-nav" aria-label="Primary navigation">
        {navLinks.map((link) => (
          <a key={link.label} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
    </header>
  );
};

export default LoginHeader;

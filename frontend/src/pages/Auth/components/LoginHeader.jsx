import React from "react";
import { Link } from "react-router-dom";

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
      <Link className="auth-logo" to="/" aria-label="AutoAudit home">
        <img src="/AutoAudit.png" alt="AutoAudit" />
      </Link>

      <nav className="auth-nav" aria-label="Primary navigation">
        {navLinks.map((link) =>
          link.href.startsWith("/") ? (
            <Link key={link.label} to={link.href}>
              {link.label}
            </Link>
          ) : (
            <a key={link.label} href={link.href}>
              {link.label}
            </a>
          )
        )}
      </nav>
    </header>
  );
};

export default LoginHeader;

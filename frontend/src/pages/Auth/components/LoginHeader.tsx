import React from "react";
import { Link } from "react-router-dom";

const navLinks: { label: string; href: string }[] = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const LoginHeader = () => {
  return (
    <header className="flex items-center justify-between border-b border-white/10 bg-[rgb(var(--landing-bg-base)/0.95)] px-[5%] py-6 backdrop-blur-[10px]">
      <Link to="/" aria-label="AutoAudit home" className="block">
        <img
          src="/AutoAudit.png"
          alt="AutoAudit"
          className="w-auto transition-transform duration-300 h-17.5 hover:scale-[1.04]"
        />
      </Link>

      <nav className="flex gap-6 items-center" aria-label="Primary navigation">
        {navLinks.map((link) =>
          link.href.startsWith("/") ? (
            <Link
              key={link.label}
              to={link.href}
              className="relative font-medium transition-colors duration-300 hover:text-blue-500 text-[rgb(224_224_224)]"
            >
              {link.label}
            </Link>
          ) : (
            <a
              key={link.label}
              href={link.href}
              className="relative font-medium transition-colors duration-300 hover:text-blue-500 text-[rgb(224_224_224)]"
            >
              {link.label}
            </a>
          )
        )}
      </nav>
    </header>
  );
};

export default LoginHeader;
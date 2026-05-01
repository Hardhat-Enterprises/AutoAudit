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
    <header className="flex items-center justify-between border-b border-white/10 bg-[rgba(10,22,40,0.95)] px-[5%] py-6 backdrop-blur-[10px]">
      <Link to="/" aria-label="AutoAudit home" className="block">
        <img
          src="/AutoAudit.png"
          alt="AutoAudit"
          className="h-17.5 w-auto transition-transform duration-300 hover:scale-[1.04]"
        />
      </Link>

      <nav className="flex items-center gap-6" aria-label="Primary navigation">
        {navLinks.map((link) =>
          link.href.startsWith("/") ? (
            <Link
              key={link.label}
              to={link.href}
              className="relative font-medium text-[#e0e0e0] transition-colors duration-300 hover:text-blue-500"
            >
              {link.label}
            </Link>
          ) : (
            <a
              key={link.label}
              href={link.href}
              className="relative font-medium text-[#e0e0e0] transition-colors duration-300 hover:text-blue-500"
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
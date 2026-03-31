import React from "react";
import { Link } from "react-router-dom";

const navLinks = [
  { label: "Home", href: "/#main-content" },
  { label: "Features", href: "/#features" },
  { label: "Benefits", href: "/#benefits" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

type LandingHeaderProps = {
  onSignInClick?: () => void;
  hiddenLinks?: string[];
  showSignIn?: boolean;
};

const LandingHeader = ({
  onSignInClick,
  hiddenLinks = [],
  showSignIn = true,
}: LandingHeaderProps) => {
  const hiddenLinkSet = new Set(hiddenLinks.map((link) => link.toLowerCase()));

  return (
    <header className="landing-header">
      <Link
        className="landing-logo"
        to="/#main-content"
        aria-label="AutoAudit home"
      >
        <picture>
          <source srcSet="/AutoAudit.webp" type="image/webp" />
          <img src="/AutoAudit.png" alt="AutoAudit" loading="lazy" />
        </picture>
      </Link>

      <nav className="landing-nav" aria-label="Primary navigation">
        {navLinks
          .filter((link) => !hiddenLinkSet.has(link.label.toLowerCase()))
          .map((link) =>
            link.href.startsWith("/") ? (
              <Link key={link.label} to={link.href}>
                {link.label}
              </Link>
            ) : (
              <a key={link.label} href={link.href}>
                {link.label}
              </a>
            ),
          )}
        {showSignIn && (
          <button
            type="button"
            onClick={onSignInClick}
            className="rounded-full bg-gradient-to-br from-[#3b82f6] to-[#2563eb] px-5 py-2.5 text-sm font-semibold text-white transition duration-200 hover:from-[#22d3ee] hover:to-[#3b82f6] hover:-translate-y-0.5 hover:shadow-[0_10px_25px_rgba(59,130,246,0.35)]"
          >
            Sign In
          </button>
        )}
      </nav>
    </header>
  );
};

export default LandingHeader;

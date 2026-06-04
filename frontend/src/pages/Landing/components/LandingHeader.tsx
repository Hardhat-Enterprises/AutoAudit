import React, { useState } from "react";
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
  const hiddenLinkSet = new Set(hiddenLinks.map((l) => l.toLowerCase()));
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* HEADER */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 bg-slate-900">
        
        {/* Left Section */}
        <div className="flex items-center gap-3">
          
          {/* Hamburger Button - Mobile Only */}
          <button
            className="md:hidden text-white text-2xl"
            onClick={() => setIsOpen(true)}
            aria-label="Open navigation menu"
          >
            ☰
          </button>

          {/* Logo */}
          <Link to="/#main-content">
            <img
              src="/AutoAudit.png"
              alt="AutoAudit"
              className="h-8 w-auto"
            />
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-white">
          {navLinks
            .filter(
              (link) => !hiddenLinkSet.has(link.label.toLowerCase())
            )
            .map((link) => (
              <Link
                key={link.label}
                to={link.href}
                className="hover:text-blue-400 transition-colors"
              >
                {link.label}
              </Link>
            ))}

          {showSignIn && (
            <button
              className="btn-primary"
              onClick={onSignInClick}
            >
              Sign In
            </button>
          )}
        </nav>
      </header>

      {/* MOBILE SIDEBAR */}
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex md:hidden">
          
          {/* Overlay */}
          <div
            className="fixed inset-0 bg-black/50"
            onClick={() => setIsOpen(false)}
          />

          {/* Sidebar */}
          <div className="relative w-64 bg-slate-900 h-full p-6 z-50 shadow-lg transition-transform duration-300">
            
            {/* Close Button */}
            <button
              className="text-white text-2xl absolute top-4 right-4"
              onClick={() => setIsOpen(false)}
              aria-label="Close navigation menu"
            >
              ✕
            </button>

            {/* Mobile Navigation */}
            <nav className="flex flex-col gap-4 text-white mt-12">
              {navLinks
                .filter(
                  (link) =>
                    !hiddenLinkSet.has(link.label.toLowerCase())
                )
                .map((link) => (
                  <Link
                    key={link.label}
                    to={link.href}
                    onClick={() => setIsOpen(false)}
                    className="hover:text-blue-400 transition-colors"
                  >
                    {link.label}
                  </Link>
                ))}

              {showSignIn && (
                <button
                  className="mt-4 w-full rounded-full bg-blue-600 px-4 py-3 text-white shadow-lg shadow-blue-500/40 hover:bg-blue-700 transition-colors"
                  onClick={() => {
                    setIsOpen(false);
                    onSignInClick?.();
                  }}
                >
                  Sign In
                </button>
              )}
            </nav>
          </div>
        </div>
      )}
    </>
  );
};

export default LandingHeader;
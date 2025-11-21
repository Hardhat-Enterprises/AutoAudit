import React from "react";

const LandingHeader = ({ onSignInClick, onAboutClick }) => {
  return (
    <header className="landing-header">
      <a className="landing-logo" href="/" aria-label="AutoAudit home">
        <img src="/logo.png" alt="AutoAudit" />
      </a>

      <nav className="landing-nav" aria-label="Primary navigation">
        <a href="#features">Features</a>
        <a href="#benefits">Benefits</a>
        <button type="button" onClick={onAboutClick} className="link-button">
          About
        </button>
        <button type="button" className="btn-primary" onClick={onSignInClick}>
          Sign In
        </button>
      </nav>
    </header>
  );
};

export default LandingHeader;

import React from "react";
import "../index.css";
import { TOKEN_META } from "../styles/tokens-meta"; // name, rbg, hex labels

// Token keys
const TOKENS = Object.keys(TOKEN_META);

// Pick a legible text color for swatch labels
// (if swatch background is a text colour, use surface-1 for contrast)
// If not, use text-strong
// Parse "R G B" → [r,g,b] (split string and convert to numbers so we can math brr)
function parseTriplet(rgb) {
  const [r, g, b] = rgb.split(/\s+/).map(Number);
  return [r, g, b];
}

// WCAG relative luminance (0 = black, 1 = white)
// formula from https://www.w3.org/TR/WCAG20/#relativeluminancedef
function relLuminance([r, g, b]) {
  const srgb = [r, g, b].map(v => v / 255); // convert RBG from 0-255 to 0-1
  const lin = srgb.map(v => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}

// For the current theme section, choose a token that is "light" or "dark"
function textTokenForMode(mode, wantLightText) {
  // In dark mode: light text = text-strong, dark text = surface-1
  // In light mode: light text = surface-1, dark text = text-strong
  if (mode === "dark") return wantLightText ? "var(--text-strong)" : "var(--surface-1)";
  return wantLightText ? "var(--surface-1)" : "var(--text-strong)";
}


function Swatch({ token, mode }) {
  const meta = TOKEN_META[token];
  const info = mode === "light" && meta.light ? meta.light : meta;
  // If in light mode and there’s a meta.light override, use it. Otherwise use  default.

  // Compute background luminance from the token's RGB for this mode
  const bgL = relLuminance(parseTriplet(info.rgb));

  // If background is dark (luminance < 0.5), use light text
  const wantLightText = bgL < 0.5;

  // Pick the correct text token for the current mode
  const labelText = textTokenForMode(mode, wantLightText);

  return (
    <div
      className="flex flex-col items-center justify-center h-28 rounded text-center p-2"
      style={{
        background: `rgb(var(--${token}))`,     // paint with CSS var so .light works
        color: `rgb(${labelText})`,             // computed for contrast
        border: `1px solid rgb(var(--border-subtle))`
      }}
    >
      <span className="font-semibold">{token}</span>
      <span className="text-xs opacity-90">{info.name}</span>
      <span className="text-xs opacity-75">rgb({info.rgb})</span>
      <span className="text-xs opacity-75">{info.hex}</span>
    </div>
  );
}


export default function StyleGuide() {
  return (
    <div className="min-h-screen">
      {/* Dark mode section */}
      <section
        className="p-6 space-y-4"
        style={{
          background: "rgb(var(--surface-1))",
          color: "rgb(var(--text-strong))"
        }}
      >
        <h2 className="text-xl font-semibold">Dark Mode</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {TOKENS.map((t) => (
            <Swatch key={`dark-${t}`} token={t} mode="dark" />
          ))}
        </div>
      </section>

      {/* Light mode section */}
      <section
        className="light p-6 space-y-4"
        style={{
          background: "rgb(var(--surface-1))",
          color: "rgb(var(--text-strong))"
        }}
      >
        <h2 className="text-xl font-semibold">Light Mode</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {TOKENS.map((t) => (
            <Swatch key={`light-${t}`} token={t} mode="light" />
          ))}
        </div>
      </section>
    </div>
  );
}
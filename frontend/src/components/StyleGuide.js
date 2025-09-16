import React from "react";
import "../index.css";
import { TOKEN_META } from "../styles/tokens-meta"; // name, rbg, hex labels

// Token keys
const TOKENS = Object.keys(TOKEN_META);

// Pick a legible text color for swatch labels
// (if swatch background is a text colour, use surface-1 for contrast)
// If not, use text-strong
function labelTextVar(token) {
  return token.startsWith("text-") ? "var(--surface-1)" : "var(--text-strong)";
}

function Swatch({ token, mode }) {
  const meta = TOKEN_META[token];
  // Use light variant if in light mode and it exists
  // If not, use default (dark) values
  const info = mode === "light" && meta.light ? meta.light : meta;

  return (
    <div
      className="flex flex-col items-center justify-center h-28 rounded text-center p-2"
      style={{
        background: `rgb(var(--${token}))`,
        color: `rgb(${labelTextVar(token)})`,
        border: `1px solid rgb(var(--border-subtle))` // add border so it does not blend into background
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
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
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
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {TOKENS.map((t) => (
            <Swatch key={`light-${t}`} token={t} mode="light" />
          ))}
        </div>
      </section>
    </div>
  );
}
const withOpacity = (varName) => ({ opacityValue }) =>
  opacityValue === undefined
    ? `rgb(var(${varName}))`
    : `rgb(var(${varName}) / ${opacityValue})`;

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx,html}"],
  theme: {
    extend: {
      colors: {
        surface: {
          1: withOpacity("--surface-1"),
          2: withOpacity("--surface-2"),
        },
        border: {
          subtle: withOpacity("--border-subtle"),
        },
        text: {
          strong: withOpacity("--text-strong"),
          muted: withOpacity("--text-muted"),
        },
        accent: {
          teal: withOpacity("--accent-teal"),
          navy: withOpacity("--accent-navy"),
          good: withOpacity("--accent-good"),
          warn: withOpacity("--accent-warn"),
          bad:  withOpacity("--accent-bad"),
        },
      },
      borderRadius: {
        card: "var(--radius-2)", // pick 2 as default card
      },
      boxShadow: {
        // optional: token shadows (not in use just yet)
        "elev-1": "var(--shadow-1)",
        "elev-2": "var(--shadow-2)",
      },
      fontFamily: {
        header: ['"League Spartan"', "ui-sans-serif", "system-ui", "Segoe UI", "Inter", "Arial"],
        body: ["Segoe UI", "ui-sans-serif", "system-ui", "Inter", "Arial"],
        mono: ["ui-monospace","SFMono-Regular","Menlo","Consolas","monospace"],
      },
    },
  },
  plugins: [],
};

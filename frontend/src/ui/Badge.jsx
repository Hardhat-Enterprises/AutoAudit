import React from "react";

export function Badge({ children, tone = "neutral", className = "" }) {
  const bg =
    tone === "critical"
      ? "var(--accent-bad)"
      : tone === "high" || tone === "medium"
      ? "var(--accent-warn)"
      : tone === "success"
      ? "var(--accent-good)"
      : "var(--border-subtle)";

  return (
    <span
      className={className}
      style={{
        display: "inline-block",
        background: `rgb(${bg})`,
        color: "rgb(var(--surface-1))",
        borderRadius: "var(--radius-1)",
        padding: "2px 8px",
        fontSize: "12px",
        lineHeight: 1.4,
        fontWeight: 600,
      }}
    >
      {children}
    </span>
  );
}

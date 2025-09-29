import React from "react";

const toneMap = {
  good: "tone-good",
  warn: "tone-warn",
  bad:  "tone-bad",
  muted:"tone-muted",
};

/**
 * Token-aware Card
 * Props:
 *  - tone: 'good' | 'warn' | 'bad' | 'muted' (adds the left border tone)
 *  - as: element type (default 'div') — optional
 *  - className: extra classes
 */
export default function Card({ tone = "muted", as: As = "div", className = "", children, ...props }) {
  const toneClass = toneMap[tone] ?? toneMap.muted;
  return (
    <As className={`card ${toneClass} ${className}`} {...props}>
      {children}
    </As>
  );
}

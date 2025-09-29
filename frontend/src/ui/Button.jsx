import React from "react";

export default function Button({
  as: As = "button",
  variant = "primary", // 'primary' | 'secondary' | 'ghost'
  size = "md",         // 'sm' | 'md' | 'lg'
  className = "",
  children,
  ...props
}) {
  const base =
    "inline-flex items-center justify-center font-header rounded-card border transition " +
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const sizes = {
    sm: "h-9 px-3 text-sm",
    md: "h-11 px-5 text-base",
    lg: "h-14 px-7 text-xl",
  };
  const variants = {
    primary:   "bg-accent-teal text-surface-1 border-accent-teal hover:bg-accent-teal/90",
    secondary: "bg-surface-2/80 text-text-strong border-border-subtle hover:bg-surface-2",
    ghost:     "bg-transparent text-text-muted border-border-subtle hover:bg-text-muted/10",
  };

  return (
    <As className={`${base} ${sizes[size]} ${variants[variant]} ${className}`} {...props}>
      {children}
    </As>
  );
}

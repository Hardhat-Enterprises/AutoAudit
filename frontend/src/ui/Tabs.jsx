import React, { createContext, useContext, useState } from "react";

const TabsCtx = createContext(null);

export function Tabs({ defaultValue, children, className = "" }) {
  const [value, setValue] = useState(defaultValue);
  return (
    <TabsCtx.Provider value={{ value, setValue }}>
      <div className={className}>{children}</div>
    </TabsCtx.Provider>
  );
}

export function TabsList({ children, className = "", style }) {
  return (
    <div
      className={className}
      style={{
        display: "grid",
        gridAutoFlow: "column",
        gap: 8,
        padding: 6,
        borderRadius: "var(--radius-1)",
        background: "rgb(var(--surface-2))",
        border: "1px solid rgb(var(--border-subtle))",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({ value, children, className = "" , style }) {
  const ctx = useContext(TabsCtx);
  const active = ctx?.value === value;
  return (
    <button
      onClick={() => ctx.setValue(value)}
      className={className}
      style={{
        padding: "8px 12px",
        borderRadius: "var(--radius-1)",
        border: "1px solid rgb(var(--border-subtle))",
        background: active ? "rgb(var(--accent-teal))" : "transparent",
        color: active ? "rgb(var(--surface-1))" : "rgb(var(--text-strong))",
        fontWeight: 600,
        ...style,
      }}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className = "" }) {
  const ctx = useContext(TabsCtx);
  if (ctx?.value !== value) return null;
  return <div className={className} style={{ marginTop: 16 }}>{children}</div>;
}

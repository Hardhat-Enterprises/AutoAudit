import React, { createContext, useContext, useState, cloneElement } from "react";

const DialogCtx = createContext(null);

export function Dialog({ children }) {
  const [open, setOpen] = useState(false);
  return (
    <DialogCtx.Provider value={{ open, setOpen }}>
      {children}
    </DialogCtx.Provider>
  );
}

export function DialogTrigger({ asChild, children }) {
  const { setOpen } = useContext(DialogCtx);
  if (asChild && React.isValidElement(children)) {
    return cloneElement(children, {
      onClick: (e) => {
        children.props.onClick?.(e);
        setOpen(true);
      },
    });
  }
  return (
    <button onClick={() => setOpen(true)}>
      {children}
    </button>
  );
}

export function DialogContent({ children, className = "", style }) {
  const { open, setOpen } = useContext(DialogCtx);
  if (!open) return null;
  return (
    <div
      onClick={() => setOpen(false)}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,.45)",
        zIndex: 60,
        display: "grid",
        placeItems: "center",
        padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className={className}
        style={{
          width: "min(1200px, 96vw)",
          maxHeight: "95vh",
          overflowY: "auto",
          background: "rgb(var(--surface-1))",
          border: "1px solid rgb(var(--border-subtle))",
          borderRadius: "var(--radius-2)",
          ...style,
        }}
      >
        {children}
      </div>
    </div>
  );
}

export function DialogHeader({ children, className = "" }) {
  return <div className={`p-5 ${className}`}>{children}</div>;
}

export function DialogTitle({ children, className = "" }) {
  return (
    <h2
      className={className}
      style={{ color: "rgb(var(--text-strong))", fontWeight: 700 }}
    >
      {children}
    </h2>
  );
}

export function DialogDescription({ children, className = "" }) {
  return (
    <p
      className={className}
      style={{ color: "rgb(var(--text-muted))" }}
    >
      {children}
    </p>
  );
}

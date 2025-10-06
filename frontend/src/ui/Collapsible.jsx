import React, { useState } from "react";

export function Collapsible({ open: controlled, defaultOpen = false, children }) {
  const [uncontrolledOpen, setOpen] = useState(defaultOpen);
  const open = controlled ?? uncontrolledOpen;
  return <div data-open={open ? "true" : "false"}>{children}</div>;
}

export function CollapsibleTrigger({ onClick, children }) {
  return <button onClick={onClick} style={{ padding: 6 }}>{children}</button>;
}

export function CollapsibleContent({ children, className = "" }) {
  return <div className={className} style={{ marginTop: 8 }}>{children}</div>;
}

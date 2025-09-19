// xss-test.js
// ❌ Vulnerable: uses user input directly inside dangerouslySetInnerHTML
import React from "react";

export default function XssTest() {
  // read `?msg=` from URL (simulates user-provided data)
  const params = new URLSearchParams(window.location.search);
  const msg = params.get("msg") || "Hello, safe default";

  // Vulnerable: putting raw user input into innerHTML
  return (
    <div style={{ padding: 16 }}>
      <h3>Vulnerable XSS demo</h3>
      <div
        data-testid="vulnerable-output"
        dangerouslySetInnerHTML={{ __html: msg }}
      />
      <p>Open this page with ?msg=... to see the effect.</p>
    </div>
  );
}

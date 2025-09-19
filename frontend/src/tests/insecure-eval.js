// insecure-eval.js
// ❌ Vulnerable: running eval() on user input
// This file exports a tiny function and uses a query param to demonstrate misuse.

export function runUserCodeFromQuery() {
    try {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code") || "2 + 2"; // user-supplied code
  
      // Vulnerable: evaluate arbitrary user code
      // eslint-disable-next-line no-eval
      const result = eval(code);
  
      return { ok: true, code, result };
    } catch (err) {
      return { ok: false, error: String(err) };
    }
  }
  
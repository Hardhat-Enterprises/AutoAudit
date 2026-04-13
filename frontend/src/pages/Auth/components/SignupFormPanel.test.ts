import { describe, it, expect } from "vitest";

// Inline the function here to test it in isolation without importing JSX
const getPasswordStrength = (password: string) => {
  if (!password) return null;
  if (password.length < 6) return { label: "Weak", level: 1 };
  let score = 0;
  if (password.length >= 10) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  if (score <= 1) return { label: "Weak", level: 1 };
  if (score === 2) return { label: "Fair", level: 2 };
  if (score === 3) return { label: "Good", level: 3 };
  return { label: "Strong", level: 4 };
};

describe("getPasswordStrength", () => {
  it("returns null for empty string", () => {
    expect(getPasswordStrength("")).toBeNull();
  });

  it("returns Weak for passwords shorter than 6 characters regardless of complexity", () => {
    expect(getPasswordStrength("A1!")).toEqual({ label: "Weak", level: 1 });
    expect(getPasswordStrength("Ab1!")).toEqual({ label: "Weak", level: 1 });
  });

  it("returns Weak for a simple short-ish password with no complexity", () => {
    expect(getPasswordStrength("abcdef")).toEqual({ label: "Weak", level: 1 });
  });

  it("returns Fair for a 6+ char password with 2 complexity points", () => {
    // length < 10 (no score), uppercase (1), number (1) = score 2
    expect(getPasswordStrength("Abc123")).toEqual({ label: "Fair", level: 2 });
  });

  it("returns Good for a 6+ char password with 3 complexity points", () => {
    // uppercase (1), number (1), special (1) = score 3
    expect(getPasswordStrength("Abc12!")).toEqual({ label: "Good", level: 3 });
  });

  it("returns Strong for a 10+ char password with all complexity points", () => {
    // length >= 10 (1), uppercase (1), number (1), special (1) = score 4
    expect(getPasswordStrength("Abcdef123!")).toEqual({ label: "Strong", level: 4 });
  });

  it("does not give Strong to a long password with no complexity", () => {
    // length >= 10 (1), no other points = score 1 → Weak
    expect(getPasswordStrength("abcdefghij")).toEqual({ label: "Weak", level: 1 });
  });
});

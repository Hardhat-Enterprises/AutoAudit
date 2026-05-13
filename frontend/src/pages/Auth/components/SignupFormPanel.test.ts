import { describe, it, expect } from "vitest";
import { getPasswordStrength } from "./SignupFormPanel";

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
    expect(getPasswordStrength("Abc123")).toEqual({ label: "Fair", level: 2 });
  });

  it("returns Good for a 6+ char password with 3 complexity points", () => {
    expect(getPasswordStrength("Abc12!")).toEqual({ label: "Good", level: 3 });
  });

  it("returns Strong for a 10+ char password with all complexity points", () => {
    expect(getPasswordStrength("Abcdef123!")).toEqual({ label: "Strong", level: 4 });
  });

  it("does not give Strong to a long password with no complexity", () => {
    expect(getPasswordStrength("abcdefghij")).toEqual({ label: "Weak", level: 1 });
  });
});

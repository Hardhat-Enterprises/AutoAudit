import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Loader2 } from "lucide-react";

import "./LoginPage.css";
import "../Landing/LandingPage.css";

import LoginHeader from "./components/LoginHeader";
import BrandPanel from "./components/BrandPanel";
import LandingFooter from "../Landing/components/LandingFooter";
import { useAuth } from "../../context/AuthContext";

const CALLBACK_CACHE_KEY = "autoaudit.oauth.google.callback.params";

function safeJsonParse(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function readCachedCallbackParams() {
  if (typeof window === "undefined") return null;
  try {
    return safeJsonParse(window.sessionStorage.getItem(CALLBACK_CACHE_KEY));
  } catch {
    return null;
  }
}

function writeCachedCallbackParams(payload) {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(CALLBACK_CACHE_KEY, JSON.stringify(payload));
  } catch {
    // best-effort
  }
}

function clearCachedCallbackParams() {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(CALLBACK_CACHE_KEY);
  } catch {
    // best-effort
  }
}

function getOAuthParams() {
  const rawHash = typeof window !== "undefined" ? window.location.hash : "";
  const hash = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
  const merged = new URLSearchParams(hash);

  // Some environments/providers return parameters in the query string.
  const rawSearch = typeof window !== "undefined" ? window.location.search : "";
  const search = rawSearch.startsWith("?") ? rawSearch.slice(1) : rawSearch;
  const searchParams = new URLSearchParams(search);
  for (const [key, value] of searchParams.entries()) {
    if (!merged.has(key)) merged.set(key, value);
  }

  return merged;
}

const GoogleCallbackPage = () => {
  const navigate = useNavigate();
  const auth = useAuth();

  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function finish() {
      const params = getOAuthParams();

      // Prefer params from the URL, but fall back to a cached copy.
      // React 18 StrictMode intentionally mounts effects twice in development; the first
      // run clears the hash, so the second run would otherwise see no token.
      const urlPayload = {
        access_token: params.get("access_token") || params.get("token") || params.get("accessToken"),
        token_type: params.get("token_type") || params.get("tokenType"),
        error: params.get("error"),
        error_description: params.get("error_description") || params.get("errorDescription"),
      };

      if (urlPayload.access_token || urlPayload.error) {
        writeCachedCallbackParams(urlPayload);
      }

      const cachedPayload = readCachedCallbackParams();
      const accessToken = urlPayload.access_token || cachedPayload?.access_token;
      const oauthError = urlPayload.error || cachedPayload?.error;
      const oauthErrorDescription =
        urlPayload.error_description || cachedPayload?.error_description;

      if (oauthError) {
        if (!cancelled) {
          setError(oauthErrorDescription || oauthError);
        }
        clearCachedCallbackParams();
        return;
      }

      if (!accessToken) {
        if (!cancelled) {
          setError("Missing access token. Please try signing in again.");
        }
        clearCachedCallbackParams();
        return;
      }

      // Remove the token fragment from the URL as soon as possible.
      try {
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch {
        // best-effort
      }

      try {
        // SSO sessions must use sessionStorage (remember=false).
        await auth.loginWithAccessToken(accessToken, false);
        clearCachedCallbackParams();
        if (!cancelled) {
          // Hard redirect so we always leave the callback page after external OAuth.
          window.location.replace("/dashboard");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err?.message || "Google sign-in failed. Please try again.");
        }
        clearCachedCallbackParams();
      }
    }

    finish();
    return () => {
      cancelled = true;
    };
    // We intentionally run this effect only once on initial load of the callback page.
    // AuthContext updates after login would otherwise re-run the effect and the URL
    // hash may already be cleared, leading to a false “missing access token” error.
  }, []);

  return (
    <div className="login-page">
      <LoginHeader />
      <main className="login-main">
        <BrandPanel />
        <section className="login-form-section">
          <div className="login-form-card">
            {error ? (
              <>
                <div className="login-form-header">
                  <h2>Sign-in failed</h2>
                  <p>We couldn’t complete Google sign-in. Please try again.</p>
                </div>
                <div
                  className="error-message"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "12px",
                    backgroundColor: "rgba(239, 68, 68, 0.1)",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    borderRadius: "8px",
                    color: "#ef4444",
                    marginTop: "24px",
                    marginBottom: "16px",
                  }}
                >
                  <AlertCircle size={18} />
                  <span>{error}</span>
                </div>

                <button
                  type="button"
                  className="btn-signin"
                  onClick={() => navigate("/login")}
                >
                  Back to sign in
                </button>
              </>
            ) : (
              <div
                style={{
                  marginTop: "10px",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "12px",
                  minHeight: "140px",
                  color: "#b0c4de",
                }}
              >
                <Loader2
                  size={28}
                  className="animate-spin"
                  style={{ animation: "spin 1s linear infinite" }}
                />
                <div style={{ fontSize: "14px" }}>Please wait while we sign you in.</div>
              </div>
            )}
          </div>
        </section>
      </main>
      <LandingFooter />
    </div>
  );
};

export default GoogleCallbackPage;



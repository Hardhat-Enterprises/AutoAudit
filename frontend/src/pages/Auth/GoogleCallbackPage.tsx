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

type OAuthCallbackPayload = {
  access_token?: string | null;
  token_type?: string | null;
  error?: string | null;
  error_description?: string | null;
}

function safeJsonParse(value: string | null): unknown {
  if (!value) return null;
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function readCachedCallbackParams(): OAuthCallbackPayload | null {
  if (typeof window === "undefined") return null;
  try {
    const parsed = safeJsonParse(window.sessionStorage.getItem(CALLBACK_CACHE_KEY));
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as OAuthCallbackPayload;
    }
    return null;
  } catch {
    return null;
  }
}

function writeCachedCallbackParams(payload: OAuthCallbackPayload): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(CALLBACK_CACHE_KEY, JSON.stringify(payload));
  } catch {
    // best-effort
  }
}

function clearCachedCallbackParams(): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(CALLBACK_CACHE_KEY);
  } catch {
    // best-effort
  }
}

function getOAuthParams(): URLSearchParams {
  const rawHash = typeof window !== "undefined" ? window.location.hash : "";
  const hash = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
  const merged = new URLSearchParams(hash);

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

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function finish() {
      const params = getOAuthParams();

      const urlPayload: OAuthCallbackPayload = {
        access_token:
          params.get("access_token") || params.get("token") || params.get("accessToken"),
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
      const oauthErrorDescription = urlPayload.error_description || cachedPayload?.error_description;

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

      try {
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch {
        // best-effort
      }

      try {
        await auth.loginWithAccessToken(accessToken, false);
        clearCachedCallbackParams();
        if (!cancelled) {
          window.location.replace("/dashboard");
        }
      } catch (err) {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : "Google sign-in failed. Please try again.";
          setError(msg);
        }
        clearCachedCallbackParams();
      }
    }

    void finish();
    return () => {
      cancelled = true;
    };
    // Intentionally run once on mount — see comment in original implementation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

                <button type="button" className="btn-signin" onClick={() => navigate("/login")}>
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

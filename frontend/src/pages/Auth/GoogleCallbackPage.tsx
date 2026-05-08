import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Loader2 } from "lucide-react";

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
};

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
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[rgb(8_27_46)]">
      <LoginHeader />
      <main className="flex flex-1 justify-center items-center py-12 px-6">
        <div className="grid gap-10 w-full max-w-6xl lg:grid-cols-2">
          <div className="hidden justify-center items-center lg:flex">
            <BrandPanel />
          </div>

          <section className="flex justify-center items-center">
            <div className="p-9 w-full max-w-[480px] rounded-[18px] bg-[rgb(15_35_56/0.9)] shadow-[0_30px_60px_rgb(5_9_20/0.45)]">
              {error ? (
                <>
                  <div>
                    <h2 className="mb-2 text-3xl font-semibold text-white">Sign-in failed</h2>
                    <p className="text-slate-300">
                      We couldn&apos;t complete Google sign-in. Please try again.
                    </p>
                  </div>

                  <div className="flex gap-2 items-center py-3 px-3 mt-6 mb-4 text-red-400 rounded-lg border border-red-500/30 bg-red-500/10">
                    <AlertCircle size={18} />
                    <span>{error}</span>
                  </div>

                  <button
                    type="button"
                    className="flex gap-2 justify-center items-center py-4 px-4 w-full text-base font-semibold text-white bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl transition hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgb(var(--brand-blue)/0.4)]"
                    onClick={() => navigate("/login")}
                  >
                    Back to sign in
                  </button>
                </>
              ) : (
                <div className="flex flex-col gap-3 justify-center items-center mt-2 min-h-[140px] text-[rgb(var(--landing-text-soft))]">
                  <Loader2 size={28} className="animate-spin" />
                  <div className="text-sm">Please wait while we sign you in.</div>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
      <LandingFooter />
    </div>
  );
};

export default GoogleCallbackPage;
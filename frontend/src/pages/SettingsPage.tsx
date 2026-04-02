import React, { useEffect, useState } from "react";
import { AlertCircle, Loader2, Settings } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getSettings, updateSettings } from "../api/client";

type SettingsPageProps = {
  sidebarWidth?: number;
  isDarkMode?: boolean;
};

const secondaryButtonClass =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-[rgb(var(--border-subtle))] bg-surface-2 px-4 py-2 text-sm font-medium text-text-strong transition-all duration-300 hover:-translate-y-px hover:bg-[rgb(var(--border-subtle))] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0";

const primaryButtonClass =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-[rgb(var(--accent-teal)/0.4)] bg-[rgb(var(--accent-teal))] px-4 py-2 text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:-translate-y-px hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0";

export default function SettingsPage({ sidebarWidth = 220, isDarkMode = true }: SettingsPageProps) {
  const { token } = useAuth();
  const [confirmDeleteEnabled, setConfirmDeleteEnabled] = useState(true);
  const [draftConfirmDeleteEnabled, setDraftConfirmDeleteEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const settings = await getSettings(token);
        const enabled = settings?.confirm_delete_enabled ?? true;
        setConfirmDeleteEnabled(enabled);
        setDraftConfirmDeleteEnabled(enabled);
      } catch (err) {
        setConfirmDeleteEnabled(true);
        setDraftConfirmDeleteEnabled(true);
        setError(err instanceof Error ? err.message : "Failed to load settings");
      } finally {
        setIsLoading(false);
      }
    }

    load();
  }, [token]);

  const hasChanges = draftConfirmDeleteEnabled !== confirmDeleteEnabled;

  function handleToggleConfirmDelete(e: React.ChangeEvent<HTMLInputElement>) {
    setDraftConfirmDeleteEnabled(e.target.checked);
  }

  async function handleSave() {
    if (!hasChanges || isSaving) {
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const updated = await updateSettings(token, {
        confirm_delete_enabled: draftConfirmDeleteEnabled,
      });
      const enabled = updated?.confirm_delete_enabled ?? draftConfirmDeleteEnabled;
      setConfirmDeleteEnabled(enabled);
      setDraftConfirmDeleteEnabled(enabled);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update settings");
    } finally {
      setIsSaving(false);
    }
  }

  function handleReset() {
    setDraftConfirmDeleteEnabled(confirmDeleteEnabled);
  }

  return (
    <div
      className={`min-h-screen bg-surface-1 p-6 text-text-strong transition-colors duration-300 ${!isDarkMode ? "light" : ""}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: "margin-left 0.4s ease, width 0.4s ease",
      }}
    >
      <div className="mx-auto flex max-w-[1000px] flex-col gap-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-text-strong">
            <Settings size={24} className="shrink-0 text-[rgb(var(--accent-teal))]" aria-hidden />
            <div>
              <h1 className="font-header text-2xl font-bold">Settings</h1>
              <p className="mt-0 text-sm text-muted">Workspace preferences and application settings.</p>
            </div>
          </div>
        </div>

        {error ? (
          <div
            className="flex items-center gap-2 rounded-lg border border-[rgb(var(--accent-bad)/0.35)] bg-[rgb(var(--accent-bad)/0.1)] px-4 py-3 text-sm text-[rgb(var(--accent-bad))]"
            role="alert"
          >
            <AlertCircle size={18} className="shrink-0" aria-hidden />
            <span>{error}</span>
          </div>
        ) : null}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center px-5 py-16 text-muted">
            <Loader2 size={32} className="animate-spin" aria-hidden />
            <p className="mt-4 text-sm">Loading settings...</p>
          </div>
        ) : (
          <div className="card">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex min-w-0 flex-col gap-1">
                <div className="text-sm font-semibold text-text-strong">Confirm before delete</div>
                <div className="text-[13px] leading-snug text-muted">
                  Show a confirmation dialog before deleting scans.
                </div>
              </div>
              <label
                className="relative inline-block h-[26px] w-[50px] shrink-0 cursor-pointer has-[:disabled]:cursor-not-allowed has-[:disabled]:opacity-50"
                aria-label="Confirm before delete"
              >
                <input
                  type="checkbox"
                  className="peer sr-only"
                  checked={draftConfirmDeleteEnabled}
                  onChange={handleToggleConfirmDelete}
                  disabled={isSaving}
                />
                <span
                  className="absolute inset-0 rounded-[26px] bg-[rgb(var(--text-muted)/0.45)] transition-colors peer-checked:bg-[rgb(var(--accent-teal))]"
                  aria-hidden
                />
                <span
                  className="absolute left-[3px] top-[3px] h-5 w-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-[24px]"
                  aria-hidden
                />
              </label>
            </div>

            <div className="mt-4 flex flex-wrap justify-end gap-3">
              <button
                type="button"
                className={secondaryButtonClass}
                onClick={handleReset}
                disabled={!hasChanges || isSaving}
              >
                Reset
              </button>
              <button
                type="button"
                className={primaryButtonClass}
                onClick={handleSave}
                disabled={!hasChanges || isSaving}
              >
                {isSaving ? (
                  <>
                    <Loader2 size={16} className="animate-spin" aria-hidden />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Save</span>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

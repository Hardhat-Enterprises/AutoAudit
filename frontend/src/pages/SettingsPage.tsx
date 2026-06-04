import React, { useEffect, useState } from "react";
import { AlertCircle, Loader2, Settings } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getSettings, updateSettings } from "../api/client";

type SettingsPageProps = {
  sidebarWidth?: number;
  isDarkMode?: boolean;
};

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
      className={`min-h-screen bg-surface-1 p-4 pl-24 text-text-strong transition-colors duration-300 sm:p-6 sm:pl-6 ${!isDarkMode ? "light" : ""}`}
      style={{
  marginLeft: sidebarWidth ? `${sidebarWidth}px` : 0,
  width: sidebarWidth ? `calc(100% - ${sidebarWidth}px)` : "100%",
  transition: "margin-left 0.4s ease, width 0.4s ease",
    }}
    >
      <div className="flex flex-col gap-6 mx-auto max-w-250">
        <div className="flex justify-between items-center">
          <div className="flex gap-4 items-center text-text-strong">
            <Settings size={24} className="shrink-0 text-accent-teal" aria-hidden />
            <div>
              <h1 className="text-2xl font-bold font-header">Settings</h1>
              <p className="mt-0 text-sm text-muted">Workspace preferences and application settings.</p>
            </div>
          </div>
        </div>

        {error ? (
          <div
            className="flex gap-2 items-center py-3 px-4 text-sm rounded-lg border border-[rgb(var(--accent-bad)/0.35)] bg-[rgb(var(--accent-bad)/0.1)] text-accent-bad"
            role="alert"
          >
            <AlertCircle size={18} className="shrink-0" aria-hidden />
            <span>{error}</span>
          </div>
        ) : null}

        {isLoading ? (
          <div className="flex flex-col justify-center items-center py-16 px-5 text-muted">
            <Loader2 size={32} className="animate-spin" aria-hidden />
            <p className="mt-4 text-sm">Loading settings...</p>
          </div>
        ) : (
          <div className="card bg-secondary">
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-center">
              <div className="flex flex-col gap-1 min-w-0">
                <div className="text-sm font-semibold text-text-strong">Confirm before delete</div>
                <div className="leading-snug text-[13px] text-muted">
                  Show a confirmation dialog before deleting scans.
                </div>
              </div>
              <label
                className="inline-block relative cursor-pointer h-6.5 w-12.5 shrink-0 has-disabled:cursor-not-allowed has-disabled:opacity-50"
                aria-label="Confirm before delete"
              >
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={draftConfirmDeleteEnabled}
                  onChange={handleToggleConfirmDelete}
                  disabled={isSaving}
                />
                <span
                  className="absolute inset-0 transition-colors rounded-[26px] bg-[rgb(var(--text-muted)/0.45)] peer-checked:bg-accent-teal"
                  aria-hidden
                />
                <span
                  className="absolute w-5 h-5 bg-white rounded-full shadow transition-transform left-0.75 top-0.75 peer-checked:translate-x-6"
                  aria-hidden
                />
              </label>
            </div>

            <div className="flex flex-col gap-3 mt-4 sm:flex-row sm:justify-end">
              <button
                type="button"
                className="inline-flex gap-2 justify-center items-center py-2 px-4 w-full text-sm font-medium rounded-lg border transition-all duration-300 sm:w-auto hover:-translate-y-px disabled:opacity-50 disabled:cursor-not-allowed border-border-subtle bg-surface-2 text-text-strong hover:bg-border-subtle disabled:hover:translate-y-0">
                Reset
              </button>
              <button
                type="button"
                className="inline-flex gap-2 justify-center items-center py-2 px-4 w-full text-sm font-semibold text-white rounded-lg border shadow-lg transition-all duration-300 sm:w-auto hover:-translate-y-px disabled:opacity-50 disabled:cursor-not-allowed border-[rgb(var(--accent-teal)/0.4)] bg-accent-teal hover:brightness-105 disabled:hover:translate-y-0"
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

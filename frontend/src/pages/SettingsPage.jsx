import React, { useEffect, useState } from "react";
import { AlertCircle, Loader2, Settings } from "lucide-react";
import "./SettingsPage.css";
import { useAuth } from "../context/AuthContext";
import { getSettings, updateSettings } from "../api/client";

export default function SettingsPage({ sidebarWidth = 220, isDarkMode = true }) {
  const { token } = useAuth();
  const [confirmDeleteEnabled, setConfirmDeleteEnabled] = useState(true);
  const [draftConfirmDeleteEnabled, setDraftConfirmDeleteEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

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
        // Fail-safe: default to showing confirmations.
        setConfirmDeleteEnabled(true);
        setDraftConfirmDeleteEnabled(true);
        setError(err?.message || "Failed to load settings");
      } finally {
        setIsLoading(false);
      }
    }

    load();
  }, [token]);

  const hasChanges = draftConfirmDeleteEnabled !== confirmDeleteEnabled;

  function handleToggleConfirmDelete(e) {
    setDraftConfirmDeleteEnabled(!!e.target.checked);
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
      setError(err?.message || "Failed to update settings");
    } finally {
      setIsSaving(false);
    }
  }

  function handleReset() {
    setDraftConfirmDeleteEnabled(confirmDeleteEnabled);
  }

  return (
    <div
      className={`settings-page ${isDarkMode ? "dark" : "light"}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: "margin-left 0.4s ease, width 0.4s ease",
      }}
    >
      <div className="settings-container">
        <div className="page-header">
          <div className="header-content">
            <Settings size={24} />
            <div className="header-text">
              <h1>Settings</h1>
              <p>Workspace preferences and application settings.</p>
            </div>
          </div>
        </div>

        {error ? (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        ) : null}

        {isLoading ? (
          <div className="loading-state">
            <Loader2 size={32} className="spinning" />
            <p>Loading settings...</p>
          </div>
        ) : (
          <div className="settings-card">
            <div className="setting-row">
              <div className="setting-text">
                <div className="setting-title">Confirm before delete</div>
                <div className="setting-description">
                  Show a confirmation dialog before deleting scans.
                </div>
              </div>
              <label className="toggle-switch" aria-label="Confirm before delete">
                <input
                  type="checkbox"
                  checked={draftConfirmDeleteEnabled}
                  onChange={handleToggleConfirmDelete}
                  disabled={isSaving}
                />
                <span className="slider" />
              </label>
            </div>

            <div className="settings-actions">
              <button
                type="button"
                className="toolbar-button secondary"
                onClick={handleReset}
                disabled={!hasChanges || isSaving}
              >
                Reset
              </button>
              <button
                type="button"
                className="toolbar-button primary"
                onClick={handleSave}
                disabled={!hasChanges || isSaving}
              >
                {isSaving ? (
                  <>
                    <Loader2 size={16} className="spinning" />
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


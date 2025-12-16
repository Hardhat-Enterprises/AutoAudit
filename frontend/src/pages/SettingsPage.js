import React from "react";
import { Settings2 } from "lucide-react";
import "./SettingsPage.css";

export default function SettingsPage({ sidebarWidth = 220, isDarkMode = true }) {
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
            <Settings2 size={24} />
            <div className="header-text">
              <h1>Settings</h1>
              <p>Workspace preferences and application settings.</p>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h3>Coming soon</h3>
          <p>
            This page is a placeholder so the sidebar doesn&apos;t route you back
            to the public landing page. We can add real settings here next.
          </p>
        </div>
      </div>
    </div>
  );
}


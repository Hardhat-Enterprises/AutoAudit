import React, { useState, useEffect } from "react";
import {
  Plus,
  Link2,
  AlertCircle,
  Loader2,
  RefreshCw,
  Pencil,
  Trash2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
  APIError,
  getPlatforms,
  getConnections,
  createConnection,
  updateConnection,
  deleteConnection,
  testConnection,
} from "../../api/client";

const CLIENT_SECRET_MASK = "************";

type FormData = {
  name: string;
  platform_id: string;
  tenant_id: string;
  client_id: string;
  client_secret: string;
};

type EditFormData = {
  name: string;
  tenant_id: string;
  client_id: string;
  client_secret: string;
};

type Connection = {
  id: string;
  name: string;
  tenant_id: string;
  client_id: string;
};

type Platform = {
  id: string;
  display_name: string;
};

type TestResult = {
  success: boolean;
  message?: string;
  tenant_display_name?: string;
  default_domain?: string;
};

type ConnectionsPageProps = {
  sidebarWidth?: number;
  isDarkMode?: boolean;
};

const inputBaseClass =
  "w-full rounded-lg border px-3.5 py-2.5 text-sm transition focus:outline-none disabled:cursor-not-allowed disabled:opacity-60";

const ConnectionsPage: React.FC<ConnectionsPageProps> = ({
  sidebarWidth = 220,
  isDarkMode = true,
}) => {
  const { token } = useAuth();
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [formData, setFormData] = useState<FormData>({
    name: "",
    platform_id: "",
    tenant_id: "",
    client_id: "",
    client_secret: "",
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [editingConnection, setEditingConnection] = useState<Connection | null>(
    null,
  );
  const [editFormData, setEditFormData] = useState<EditFormData>({
    name: "",
    tenant_id: "",
    client_id: "",
    client_secret: "",
  });
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, TestResult>>(
    {},
  );
  const pageTheme = isDarkMode
    ? {
        page: "bg-slate-950 text-white",
        card: "bg-slate-900 border-slate-800",
        muted: "text-slate-400",
        strong: "text-slate-100",
        input:
          "bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500 focus:border-blue-400",
        empty: "bg-slate-900 border-slate-700",
      }
    : {
        page: "bg-slate-50 text-slate-900",
        card: "bg-white border-slate-200",
        muted: "text-slate-500",
        strong: "text-slate-900",
        input:
          "bg-slate-100 border-slate-200 text-slate-900 placeholder:text-slate-400 focus:border-blue-500",
        empty: "bg-white border-slate-300",
      };

  function getConnectionErrorMessage(
    err: unknown,
    fallbackMessage: string,
  ): string {
    // Backend returns 400 Bad Request when M365 auth cannot be established.
    if (err instanceof APIError && err.status === 400) {
      return "Authentication not established. Please check your tenant ID, client ID, and client secret and try again.";
    }
    if (
      err &&
      typeof err === "object" &&
      "status" in err &&
      (err as { status?: number }).status === 400
    ) {
      return "Authentication not established. Please check your tenant ID, client ID, and client secret and try again.";
    }
    if (
      err &&
      typeof err === "object" &&
      "message" in err &&
      typeof (err as { message?: string }).message === "string"
    ) {
      return (err as { message: string }).message;
    }
    return fallbackMessage;
  }

  useEffect(() => {
    loadData();
  }, [token]);

  async function loadData(): Promise<void> {
    setIsLoading(true);
    setError(null);
    try {
      const [platformsData, connectionsData] = await Promise.all([
        getPlatforms(token),
        getConnections(token),
      ]);
      setPlatforms(platformsData);
      setConnections(connectionsData);
    } catch (err) {
      setError((err as any).message || "Failed to load data");
    } finally {
      setIsLoading(false);
    }
  }

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ): void {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>,
  ): Promise<void> {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const newConnection = await createConnection(token, {
        name: formData.name,
        tenant_id: formData.tenant_id,
        client_id: formData.client_id,
        client_secret: formData.client_secret,
      });
      setConnections((prev) => [...prev, newConnection]);
      setFormData({
        name: "",
        platform_id: "",
        tenant_id: "",
        client_id: "",
        client_secret: "",
      });
      setShowForm(false);
    } catch (err) {
      setError(getConnectionErrorMessage(err, "Failed to create connection"));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleTestConnection(connection: Connection): Promise<void> {
    setTestingId(connection.id);
    setError(null);
    try {
      const result = await testConnection(token, connection.id);
      setTestResults((prev) => ({ ...prev, [connection.id]: result }));
      if (!result?.success) {
        setError(result?.message || "Connection test failed");
      }
    } catch (err) {
      const message = getConnectionErrorMessage(err, "Connection test failed");
      setError(message);
      setTestResults((prev) => ({
        ...prev,
        [connection.id]: { success: false, message },
      }));
    } finally {
      setTestingId(null);
    }
  }

  function startEditing(connection: Connection): void {
    setEditingConnection(connection);
    setEditFormData({
      name: connection.name,
      tenant_id: connection.tenant_id,
      client_id: connection.client_id,
      // Never expose the actual secret; show a mask so it doesn't look blank.
      client_secret: CLIENT_SECRET_MASK,
    });
  }

  function handleEditChange(e: React.ChangeEvent<HTMLInputElement>): void {
    const { name } = e.target;
    let { value } = e.target;

    // If the user starts typing while the masked placeholder is present,
    // ensure we don't keep the mask characters in state.
    if (
      name === "client_secret" &&
      editFormData.client_secret === CLIENT_SECRET_MASK &&
      value.startsWith(CLIENT_SECRET_MASK)
    ) {
      value = value.slice(CLIENT_SECRET_MASK.length);
    }
    setEditFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleEditSubmit(
    e: React.FormEvent<HTMLFormElement>,
  ): Promise<void> {
    e.preventDefault();
    if (!editingConnection) return;

    setIsEditing(true);
    setError(null);

    try {
      const updateData: Partial<EditFormData> = {
        name: editFormData.name,
        tenant_id: editFormData.tenant_id,
        client_id: editFormData.client_id,
      };
      // Only include client_secret if user entered a new one
      if (
        editFormData.client_secret &&
        editFormData.client_secret !== CLIENT_SECRET_MASK
      ) {
        updateData.client_secret = editFormData.client_secret;
      }

      const updatedConnection = await updateConnection(
        token,
        editingConnection.id,
        updateData,
      );
      setConnections((prev) =>
        prev.map((conn) =>
          conn.id === editingConnection.id ? updatedConnection : conn,
        ),
      );
      setEditingConnection(null);
    } catch (err) {
      setError(getConnectionErrorMessage(err, "Failed to update connection"));
    } finally {
      setIsEditing(false);
    }
  }

  function cancelEditing(): void {
    setEditingConnection(null);
    setEditFormData({
      name: "",
      tenant_id: "",
      client_id: "",
      client_secret: "",
    });
  }

  async function handleDelete(id: string): Promise<void> {
    if (
      !window.confirm(
        "Are you sure you want to delete this connection? This action cannot be undone.",
      )
    ) {
      return;
    }

    setDeletingId(id);
    setError(null);

    try {
      await deleteConnection(token, id);
      setConnections((prev) => prev.filter((conn) => conn.id !== id));
    } catch (err) {
      setError((err as any).message || "Failed to delete connection");
    } finally {
      setDeletingId(null);
    }
  }

  const buttonPrimary =
    "inline-flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60";
  const buttonSecondary = `inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60 ${
    isDarkMode
      ? "border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700"
      : "border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
  }`;
  const buttonDanger =
    "inline-flex items-center gap-2 rounded-lg border border-red-400/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-500 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-60";

  if (isLoading) {
    return (
      <div
        className={`min-h-screen p-6 transition-colors duration-300 ${pageTheme.page}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: "margin-left 0.4s ease, width 0.4s ease",
        }}
      >
        <div className="mx-auto max-w-5xl">
          <div
            className={`flex flex-col items-center justify-center px-5 py-16 ${pageTheme.muted}`}
          >
            <Loader2 size={32} className="animate-spin" />
            <p className="mt-4 text-sm">Loading connections...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`min-h-screen p-6 transition-colors duration-300 ${pageTheme.page}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: "margin-left 0.4s ease, width 0.4s ease",
      }}
    >
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <Link2 size={24} className="text-blue-400" />
            <div>
              <h1 className={`text-2xl font-bold ${pageTheme.strong}`}>
                Cloud Platforms
              </h1>
              <p className={`text-sm ${pageTheme.muted}`}>
                Manage your cloud platform connections
              </p>
            </div>
          </div>

          <button
            className={buttonPrimary}
            onClick={() => setShowForm(!showForm)}
          >
            <Plus size={16} />
            <span>Add Connection</span>
          </button>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-500">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {showForm && (
          <div className={`mb-6 rounded-xl border p-6 ${pageTheme.card}`}>
            <h3 className={`mb-5 text-lg font-semibold ${pageTheme.strong}`}>
              New Connection
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="min-w-0">
                  <label
                    htmlFor="name"
                    className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                  >
                    Connection Name
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="My M365 Connection"
                    required
                    disabled={isSubmitting}
                    className={`${inputBaseClass} ${pageTheme.input}`}
                  />
                </div>

                <div className="min-w-0">
                  <label
                    htmlFor="platform_id"
                    className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                  >
                    Platform
                  </label>
                  <select
                    id="platform_id"
                    name="platform_id"
                    value={formData.platform_id}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                    className={`${inputBaseClass} ${pageTheme.input}`}
                  >
                    <option value="">Select a platform</option>
                    {platforms.map((platform) => (
                      <option key={platform.id} value={platform.id}>
                        {platform.display_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="min-w-0">
                <label
                  htmlFor="tenant_id"
                  className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                >
                  Tenant ID
                </label>
                <input
                  id="tenant_id"
                  name="tenant_id"
                  type="text"
                  value={formData.tenant_id}
                  onChange={handleChange}
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                  required
                  disabled={isSubmitting}
                  className={`${inputBaseClass} ${pageTheme.input}`}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="min-w-0">
                  <label
                    htmlFor="client_id"
                    className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                  >
                    Client ID
                  </label>
                  <input
                    id="client_id"
                    name="client_id"
                    type="text"
                    value={formData.client_id}
                    onChange={handleChange}
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    required
                    disabled={isSubmitting}
                    className={`${inputBaseClass} ${pageTheme.input}`}
                  />
                </div>

                <div className="min-w-0">
                  <label
                    htmlFor="client_secret"
                    className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                  >
                    Client Secret
                  </label>
                  <input
                    id="client_secret"
                    name="client_secret"
                    type="password"
                    value={formData.client_secret}
                    onChange={handleChange}
                    placeholder="Enter client secret"
                    required
                    disabled={isSubmitting}
                    className={`${inputBaseClass} ${pageTheme.input}`}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  className={buttonSecondary}
                  onClick={() => setShowForm(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className={buttonPrimary}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <Plus size={16} />
                      <span>Create Connection</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {editingConnection && (
          <div className={`mb-6 rounded-xl border p-6 ${pageTheme.card}`}>
            <h3 className={`mb-5 text-lg font-semibold ${pageTheme.strong}`}>
              Edit Connection
            </h3>

            <form onSubmit={handleEditSubmit}>
              <div className="mb-4">
                <label
                  htmlFor="edit_name"
                  className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                >
                  Connection Name
                </label>
                <input
                  id="edit_name"
                  name="name"
                  type="text"
                  value={editFormData.name}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                  className={`${inputBaseClass} ${pageTheme.input}`}
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="edit_tenant_id"
                  className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                >
                  Tenant ID
                </label>
                <input
                  id="edit_tenant_id"
                  name="tenant_id"
                  type="text"
                  value={editFormData.tenant_id}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                  className={`${inputBaseClass} ${pageTheme.input}`}
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="edit_client_id"
                  className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                >
                  Client ID
                </label>
                <input
                  id="edit_client_id"
                  name="client_id"
                  type="text"
                  value={editFormData.client_id}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                  className={`${inputBaseClass} ${pageTheme.input}`}
                />
              </div>

              <div className="mb-4">
                <label
                  htmlFor="edit_client_secret"
                  className={`mb-2 block text-sm font-medium ${pageTheme.muted}`}
                >
                  Client Secret
                </label>
                <input
                  id="edit_client_secret"
                  name="client_secret"
                  type="password"
                  value={editFormData.client_secret}
                  onChange={handleEditChange}
                  placeholder="Enter a new client secret"
                  onFocus={(e) => {
                    if (e.currentTarget.value === CLIENT_SECRET_MASK) {
                      e.currentTarget.select();
                    }
                  }}
                  disabled={isEditing}
                  className={`${inputBaseClass} ${pageTheme.input}`}
                />
              </div>

              <div className="mt-2 flex justify-end gap-3">
                <button
                  type="button"
                  className={buttonSecondary}
                  onClick={cancelEditing}
                  disabled={isEditing}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className={buttonPrimary}
                  disabled={isEditing}
                >
                  {isEditing ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <span>Save Changes</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {connections.length === 0 ? (
            <div
              className={`rounded-xl border border-dashed px-5 py-16 text-center ${pageTheme.empty}`}
            >
              <Link2 size={48} className={`mx-auto mb-4 ${pageTheme.muted}`} />
              <h3 className={`mb-2 text-lg font-semibold ${pageTheme.strong}`}>
                No connections yet
              </h3>
              <p className={`text-sm ${pageTheme.muted}`}>
                Add your first M365 connection to start scanning.
              </p>
            </div>
          ) : (
            connections.map((connection) => (
              <div
                key={connection.id}
                className={`flex flex-col gap-4 rounded-xl border p-5 transition hover:border-blue-400 md:flex-row md:items-center md:justify-between ${pageTheme.card}`}
              >
                <div className="flex-1">
                  <div className="mb-2 flex items-center gap-3">
                    <h4
                      className={`text-base font-semibold ${pageTheme.strong}`}
                    >
                      {connection.name}
                    </h4>

                    {testingId === connection.id ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-orange-500/15 px-2.5 py-1 text-xs font-medium text-orange-500">
                        <Loader2 size={12} className="animate-spin" />
                        <span>Testing</span>
                      </span>
                    ) : testResults[connection.id]?.success === true ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-medium text-emerald-500">
                        <CheckCircle2 size={12} />
                        <span>Connected</span>
                      </span>
                    ) : testResults[connection.id]?.success === false ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-500/15 px-2.5 py-1 text-xs font-medium text-red-500">
                        <XCircle size={12} />
                        <span>Failed</span>
                      </span>
                    ) : null}
                  </div>

                  <div
                    className={`flex flex-wrap gap-x-4 gap-y-2 text-sm ${pageTheme.muted}`}
                  >
                    <span>
                      <strong className="text-slate-400">Tenant ID:</strong>{" "}
                      {connection.tenant_id}
                    </span>
                    <span>
                      <strong className="text-slate-400">Client ID:</strong>{" "}
                      {connection.client_id}
                    </span>
                    {testResults[connection.id]?.tenant_display_name ? (
                      <span>
                        <strong className="text-slate-400">Tenant:</strong>{" "}
                        {testResults[connection.id].tenant_display_name}
                      </span>
                    ) : null}
                    {testResults[connection.id]?.default_domain ? (
                      <span>
                        <strong className="text-slate-400">
                          Default Domain:
                        </strong>{" "}
                        {testResults[connection.id].default_domain}
                      </span>
                    ) : null}
                  </div>
                </div>

                <div className="flex w-full flex-wrap gap-2 md:w-auto">
                  <button
                    className={buttonSecondary}
                    onClick={() => handleTestConnection(connection)}
                    disabled={testingId === connection.id}
                  >
                    {testingId === connection.id ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <RefreshCw size={14} />
                    )}
                    <span>
                      {testingId === connection.id ? "Testing..." : "Test"}
                    </span>
                  </button>

                  <button
                    className={buttonSecondary}
                    onClick={() => startEditing(connection)}
                    disabled={editingConnection?.id === connection.id}
                  >
                    <Pencil size={14} />
                    <span>Edit</span>
                  </button>

                  <button
                    className={buttonDanger}
                    onClick={() => handleDelete(connection.id)}
                    disabled={deletingId === connection.id}
                  >
                    {deletingId === connection.id ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <Trash2 size={14} />
                    )}
                    <span>
                      {deletingId === connection.id ? "Deleting..." : "Delete"}
                    </span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionsPage;
